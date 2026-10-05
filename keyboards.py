from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
def kb(rows):return InlineKeyboardMarkup(inline_keyboard=rows)
def start_kb(admin=False):
    r=[[InlineKeyboardButton(text='📊 Analysis',callback_data='analysis')],[InlineKeyboardButton(text='🎯 Future Signal',callback_data='future')],[InlineKeyboardButton(text='🔎 Pick',callback_data='pick')]]
    if admin:r.append([InlineKeyboardButton(text='🛠 Admin Dashboard',callback_data='admin')])
    return kb(r)
def admin_kb(enabled):return kb([[InlineKeyboardButton(text=('🟢 AUTO POST: ON' if enabled else '🔴 AUTO POST: OFF'),callback_data='toggle_auto')],[InlineKeyboardButton(text='🧠 Analysis',callback_data='analysis'),InlineKeyboardButton(text='🎯 Future',callback_data='future')],[InlineKeyboardButton(text='🔎 Pick',callback_data='pick'),InlineKeyboardButton(text='📈 Stats',callback_data='stats')],[InlineKeyboardButton(text='🔄 Refresh',callback_data='admin')]])
def market_type_kb():return kb([[InlineKeyboardButton(text='📈 LIVE MARKET',callback_data='type_live'),InlineKeyboardButton(text='🌐 OTC MARKET',callback_data='type_otc')],[InlineKeyboardButton(text='⬅️ Back',callback_data='home')]])
def analysis_mode_kb(otc=False):
    k='otc' if otc else 'live';return kb([[InlineKeyboardButton(text='⚡ Auto Detect',callback_data=f'auto_{k}')],[InlineKeyboardButton(text='🎯 Select Manually',callback_data=f'manual_{k}')],[InlineKeyboardButton(text='⬅️ Back',callback_data='analysis')]])
def confirm_auto_kb(otc):
    k='otc' if otc else 'live';return kb([[InlineKeyboardButton(text='🚀 Generate #1 Signal',callback_data=f'generate_auto_{k}')],[InlineKeyboardButton(text='⬅️ Back',callback_data=f'analysis_{k}')]])
def pair_list_kb(pairs,kind,page=0,per_page=8):
    start=page*per_page;r=[]
    for item in pairs[start:start+per_page]:
        if isinstance(item,tuple):name,payout=item;label=f'{name} ({payout}%)';key=name.replace('/','')
        else:label=item;key=item
        r.append([InlineKeyboardButton(text=label,callback_data=f'pair_{kind}_{key}')])
    nav=[]
    if page>0:nav.append(InlineKeyboardButton(text='◀️ Prev',callback_data=f'pairs_{kind}_{page-1}'))
    if start+per_page<len(pairs):nav.append(InlineKeyboardButton(text='Next ▶️',callback_data=f'pairs_{kind}_{page+1}'))
    if nav:r.append(nav)
    r.append([InlineKeyboardButton(text='⬅️ Back',callback_data=f'analysis_{kind}')]);return kb(r)
def future_kb():return kb([[InlineKeyboardButton(text='1️⃣ 1 min',callback_data='future_1'),InlineKeyboardButton(text='2️⃣ 2 min',callback_data='future_2')],[InlineKeyboardButton(text='3️⃣ 3 min',callback_data='future_3'),InlineKeyboardButton(text='4️⃣ 4 min',callback_data='future_4')],[InlineKeyboardButton(text='5️⃣ 5 min',callback_data='future_5')],[InlineKeyboardButton(text='⬅️ Back',callback_data='home')]])
def back_kb(target='home'):return kb([[InlineKeyboardButton(text='⬅️ Back',callback_data=target)]])
