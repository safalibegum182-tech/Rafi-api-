def money(x):return f'{x:.5f}'
def signal_text(s,st):
    return ('✨ <b>CB SIGNALS PRO PREMIUM</b> ✨\n\n'
            f"🕯️ <b>Asset:</b> {s['display_pair']}\n📊 <b>Trend:</b> {s['trend']}\n"
            f"🎯 <b>Signal:</b> {'🟢 CALL' if s['side']=='CALL' else '🔴 PUT'}\n📈 <b>Confidence:</b> {s['confidence']}%\n"
            f"⏳ <b>Timeframe:</b> {st.timeframe}\n⏰ <b>Entry Time:</b> {s['entry_time']}\n👑 <b>MTG:</b> Disabled\n"
            f"👤 <b>Owner:</b> {st.owner_username}\n\n💡 <b>Analysis:</b> {s['analysis']}\n\n"
            '⚠️ <i>For M1 analysis only. No outcome is guaranteed.</i>')
def result_text(s,r):
    em='🔥 WIN 🔥' if r=='WIN' else ('❌ LOSS ❌' if r=='LOSS' else '➖ DRAW')
    return ('❓ <b>TRADE RESULT</b>\n\n'
            f"🕯️ <b>Asset:</b> {s['display_pair']}\n🎯 <b>Signal:</b> {'🟢 CALL' if s['side']=='CALL' else '🔴 PUT'}\n"
            f"⏰ <b>Entry Time:</b> {s['entry_time']}\n\n{em}\n\n📉 <b>Entry:</b> {money(s['entry_price'])}\n"
            f"📈 <b>Exit:</b> {money(s['exit_price'])}\n\n✨ <b>CB SIGNALS PRO</b> ✨")
def pick_text(pair,c,a,st):
    return (f'🔎 <b>MARKET PICK</b>\n\n🕯️ <b>Asset:</b> {pair}\n⏰ <b>Candle:</b> {c.get("time","-")} ({st.timeframe})\n'
            f"🟢 <b>Open:</b> {money(c['open'])}\n📈 <b>High:</b> {money(c['high'])}\n📉 <b>Low:</b> {money(c['low'])}\n🔴 <b>Close:</b> {money(c['close'])}\n"
            f"📊 <b>Body:</b> {a['body_pct']:.1f}%\n🧭 <b>RSI:</b> {a['rsi']:.1f}\n📐 <b>EMA9/21:</b> {a['ema9']:.5f} / {a['ema21']:.5f}\n"
            f"💥 <b>ATR:</b> {a['atr']:.5f}\n\n🎯 <b>Current bias:</b> {'🟢 CALL' if a['side']=='CALL' else '🔴 PUT'}\n"
            f"📈 <b>Score:</b> {a['confidence']}%\n🧠 <b>Reasons:</b> {', '.join(a['reasons']) or 'mixed'}")
