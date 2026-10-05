import asyncio,time
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from aiogram import Router,F
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,CallbackQuery
from .config import settings,LIVE_PAIRS,OTC_CATALOG
from .keyboards import *
from .market_api import MarketAPI
from .analysis import analyze
from .formatting import signal_text,result_text,pick_text
from . import db
router=Router();api=MarketAPI(settings);jobs=set();last_signal_at=0

def is_admin(uid):return uid in settings.admin_ids
async def auto_enabled():return await db.get_setting('auto_post','1' if settings.auto_post_default else '0')=='1'
async def answer(c,t='',alert=False):
    try:await c.answer(t,show_alert=alert)
    except Exception:pass
async def edit(c,t,k=None):
    try:await c.message.edit_text(t,reply_markup=k,parse_mode='HTML')
    except Exception:await c.message.answer(t,reply_markup=k,parse_mode='HTML')
@router.message(CommandStart())
async def start(m:Message):await m.answer('✨ <b>CB SIGNALS PRO</b> ✨\n\nWelcome. Use the buttons below.',reply_markup=start_kb(is_admin(m.from_user.id)),parse_mode='HTML')
@router.message(Command('admin'))
async def admin_cmd(m:Message):
    if is_admin(m.from_user.id):await m.answer('🛠 <b>Admin Dashboard</b>',reply_markup=admin_kb(await auto_enabled()),parse_mode='HTML')
@router.callback_query(F.data=='home')
async def home(c):await answer(c);await edit(c,'✨ <b>CB SIGNALS PRO</b> ✨\n\nChoose an action.',start_kb(is_admin(c.from_user.id)))
@router.callback_query(F.data=='admin')
async def admin(c):
    if not is_admin(c.from_user.id):return await answer(c,'Admin only.',True)
    await answer(c);await edit(c,'🛠 <b>Admin Dashboard</b>',admin_kb(await auto_enabled()))
@router.callback_query(F.data=='toggle_auto')
async def toggle(c):
    if not is_admin(c.from_user.id):return await answer(c,'Admin only.',True)
    x=await auto_enabled();await db.set_setting('auto_post','0' if x else '1');await answer(c,'ON' if not x else 'OFF');await edit(c,'🛠 <b>Admin Dashboard</b>',admin_kb(not x))
@router.callback_query(F.data=='analysis')
async def analysis_menu(c):
    await answer(c);await edit(c,'🌐 <b>Select Market Type</b>\n⏰ TF: M1  |  UTC: +6  |  MTG: No MTG\n\nPick a market · live analysis generates your signal instantly.',market_type_kb())
@router.callback_query(F.data=='type_live')
async def live(c):await answer(c);await mode(c,False)
@router.callback_query(F.data=='type_otc')
async def otc(c):await answer(c);await mode(c,True)
async def mode(c,otc):
    note='\n\n⚠️ <b>OTC feed:</b> set OTC_DATA_API_URL for real OTC candles; the supplied endpoint is not documented as a Quotex OTC feed.' if otc and not settings.otc_data_api_url else ''
    await edit(c,('🌐 <b>Select Analysis Mode (%s)</b>\n⏰ TF: M1  |  UTC: +6  |  MTG: No MTG\n\n⚡ <b>Auto Detect #1 Pairs:</b> technical scanner ranks trend, momentum, RSI, EMA, candle and volume confluence.\n\n🎯 <b>Select Manual Pairs:</b> browse available pairs and payout information.%s')%('Quotex - OTC' if otc else 'LIVE MARKET',note),analysis_mode_kb(otc))
@router.callback_query(F.data.startswith('analysis_'))
async def mode_back(c):await answer(c);await mode(c,c.data.split('_',1)[1]=='otc')
@router.callback_query(F.data.startswith('auto_'))
async def auto(c):
    await answer(c);kind=c.data.split('_')[1];otc=kind=='otc'
    if otc and not settings.otc_data_api_url:return await edit(c,'⚠️ <b>OTC live data is not configured.</b>\n\nSet OTC_DATA_API_URL in .env and restart.',back_kb('analysis_otc'))
    if otc:
        e=[x for x in OTC_CATALOG if x[1]>=settings.min_payout];lst='\n'.join(f'{i+1}. {n} (OTC) ({p}%)' for i,(n,p) in enumerate(e));count=len(e)
    else:
        d=sorted([x for x in await api.discover_live(LIVE_PAIRS) if x['payout']>=settings.min_payout],key=lambda x:x['payout'],reverse=True);lst='\n'.join(f"{i+1}. {x['pair'][:3]}/{x['pair'][3:]} ({x['payout']}%)" for i,x in enumerate(d[:20])) or 'No eligible live pairs.';count=len(d)
    await edit(c,f'⚡ <b>Confirm Auto Detect (#1 Pair)</b>\n\n{count} market(s) detected (≥{settings.min_payout}% payout)\n🤖 <b>AI Asset Hunter:</b> ranks the strongest technical setup.\n📊 <b>Plan:</b> #1 high-score trade signal\nℹ️ Extra analyzed pairs are filtered before the final pick.\n\n{lst}\n\n❓ Continue to Analysis System?',confirm_auto_kb(otc))
@router.callback_query(F.data.startswith('generate_auto_'))
async def gen_auto(c):
    await answer(c,'Scanning...');r=await best(c.data.endswith('otc'))
    if not r:return await edit(c,'⚠️ No setup passed the minimum score.',back_kb())
    await publish_signal(c,r,'MANUAL')
@router.callback_query(F.data.startswith('manual_'))
async def manual(c):
    await answer(c);k=c.data.split('_',1)[1];await edit(c,'🎯 <b>Select Manual Pair</b>\n\nChoose an asset.',pair_list_kb(OTC_CATALOG if k=='otc' else LIVE_PAIRS,k))
@router.callback_query(F.data.startswith('pairs_'))
async def page(c):
    await answer(c);_,k,p=c.data.split('_');await edit(c,'🎯 <b>Select Manual Pair</b>',pair_list_kb(OTC_CATALOG if k=='otc' else LIVE_PAIRS,k,int(p)))
@router.callback_query(F.data.startswith('pair_'))
async def pair(c):
    await answer(c,'Analyzing...');_,k,p=c.data.split('_');otc=k=='otc'
    if otc and not settings.otc_data_api_url:return await edit(c,'⚠️ OTC live data is not configured.',back_kb('analysis_otc'))
    r=await analyze_pair(p,p[:3]+'/'+p[3:]+(' (OTC)' if otc else ''),otc)
    if not r:return await edit(c,'⚠️ Analysis unavailable or below score threshold.',back_kb('analysis_'+k))
    await publish_signal(c,r,'MANUAL')
@router.callback_query(F.data=='pick')
async def pick(c):
    await answer(c,'Getting current market pick...');r=await best(False)
    if not r:return await edit(c,'⚠️ No live market setup is available.',back_kb())
    _,candles=await api.fetch_closed(r['pair'],count=120);a=analyze(candles,settings.signal_min_score);await edit(c,pick_text(r['display_pair'],a['candle'],a,settings),back_kb())
@router.callback_query(F.data=='future')
async def future(c):await answer(c);await edit(c,'🎯 <b>Future Signal</b>\n\nChoose entry offset. Future outcomes are not guaranteed.',future_kb())
@router.callback_query(F.data.startswith('future_'))
async def future_m(c):
    await answer(c,'Preparing...');mins=int(c.data.split('_')[1]);r=await best(False)
    if not r:return await edit(c,'⚠️ No setup passed the current filter.',back_kb())
    r['entry_time']=(datetime.now(ZoneInfo(settings.timezone))+timedelta(minutes=mins)).strftime('%H:%M');r['signal_type']='FUTURE';await edit(c,'⏳ <b>Future signal prepared</b>\n\n'+signal_text(r,settings),back_kb())
    if is_admin(c.from_user.id):await publish_to_channel(c.bot,r)
@router.callback_query(F.data=='stats')
async def stats(c):
    if not is_admin(c.from_user.id):return await answer(c,'Admin only.',True)
    await answer(c);s=await db.stats();closed=s['win']+s['loss']+s['draw'];wr=s['win']/closed*100 if closed else 0;await edit(c,f"📈 <b>BOT STATS</b>\n\nTotal: {s['total']}\n🔥 WIN: {s['win']}\n❌ LOSS: {s['loss']}\n➖ DRAW: {s['draw']}\n🎯 Win rate: {wr:.1f}%",back_kb('admin'))
async def analyze_pair(pair,display,otc=False):
    try:
        _,c=await api.fetch_closed(pair,otc,count=300)
        if not c:return None
        a=analyze(c,settings.signal_min_score)
        if not a['eligible']:return None
        entry=(datetime.now(ZoneInfo(settings.timezone))+timedelta(minutes=1)).replace(second=0,microsecond=0)
        return {'pair':pair,'display_pair':display,'side':a['side'],'confidence':a['confidence'],'score':a['confidence'],'trend':a['trend'],'entry_price':a['entry_price'],'entry_time':entry.strftime('%H:%M'),'analysis':'Technical confluence: '+', '.join(a['reasons'])+f". RSI {a['rsi']:.1f}; EMA9/21 alignment confirmed.",'signal_type':'AUTO','otc':otc}
    except Exception:return None
async def best(otc=False):
    if otc:
        if not settings.otc_data_api_url:return None
        pairs=[x[0].replace('/','') for x in OTC_CATALOG if x[1]>=settings.min_payout]
    else:
        d=sorted([x for x in await api.discover_live(LIVE_PAIRS) if x['payout']>=settings.min_payout],key=lambda x:x['payout'],reverse=True);pairs=[x['pair'] for x in d]
    b=None
    for p in pairs[:16]:
        r=await analyze_pair(p,p[:3]+'/'+p[3:]+(' (OTC)' if otc else ''),otc)
        if r and (b is None or r['confidence']>b['confidence']):b=r
    return b
async def publish_to_channel(bot,s):
    m=await bot.send_message(settings.channel_id,signal_text(s,settings),parse_mode='HTML');s['channel_message_id']=m.message_id;i=await db.insert_signal(s);t=asyncio.create_task(track_result(bot,i,s));jobs.add(t);t.add_done_callback(jobs.discard);return m
async def publish_signal(c,s,typ='MANUAL'):
    s['signal_type']=typ;await edit(c,signal_text(s,settings),back_kb())
    if is_admin(c.from_user.id):
        try:await publish_to_channel(c.bot,s);await answer(c,'Signal posted to channel.')
        except Exception as e:await answer(c,f'Channel post failed: {e}',True)
async def track_result(bot,i,s):
    try:
        await asyncio.sleep(max(5,settings.result_delay_seconds));_,c=await api.fetch_closed(s['pair'],otc=s.get('otc',False),count=20)
        if not c:return
        target=next((x for x in c if x.get('time','').endswith(s['entry_time']+':00')),c[0]);exit_price=target['close']
        result='DRAW' if exit_price==s['entry_price'] else ('WIN' if (exit_price>s['entry_price'])== (s['side']=='CALL') else 'LOSS');s['exit_price']=exit_price;await db.update_result(i,exit_price,result);await bot.send_message(settings.channel_id,result_text(s,result),parse_mode='HTML')
    except Exception:return
async def auto_loop(bot):
    global last_signal_at
    while True:
        try:
            await asyncio.sleep(settings.auto_scan_seconds)
            if not await auto_enabled():continue
            now=datetime.now(ZoneInfo(settings.timezone))
            if now.second>12:continue
            if await db.daily_auto_count(now.strftime('%Y-%m-%d'))>=settings.max_auto_signals_per_day:continue
            if time.time()-last_signal_at<settings.min_signal_gap_seconds:continue
            s=await best(False)
            if not s:continue
            last_signal_at=time.time();await publish_to_channel(bot,s)
        except asyncio.CancelledError:raise
        except Exception:continue
