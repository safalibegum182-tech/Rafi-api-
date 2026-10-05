# CB Signals Pro

This is the requested button-driven Telegram M1 signal bot. It uses the supplied
`oandaData` endpoint for live candle data and payout filtering.

### Features
- Admin dashboard with ON/OFF automatic channel posting.
- Auto Detect and manual market analysis.
- Pick button: latest OHLC, body, RSI, EMA, ATR, bias and score.
- Future signal button: 1–5 minute entry offset.
- Automatic result verification and WIN/LOSS/DRAW post.
- SQLite history and stats.
- Bangladesh time (`Asia/Dhaka`) by default.

### Important
The endpoint inspected during development returns M1 candle data with `open`, `high`,
`low`, `close`, `colour`, `payout`, `volume`, `time` and `chart_open`. The first candle
can be the currently open candle, so the analyzer prefers closed candles.

The supplied endpoint is not documented as a Quotex OTC feed. The project therefore
requires `OTC_DATA_API_URL` for real OTC candle analysis. The 16-item OTC payout list in
the UI is a configurable catalog, not a claim that those payouts are live.

The confidence value is a technical score, not a guaranteed probability or profit claim.

### Setup
1. Create bot with BotFather.
2. Copy `.env.example` to `.env`.
3. Set `BOT_TOKEN` and your numeric Telegram ID in `ADMIN_IDS`.
4. Add the bot as an administrator of channel `-1004399158909` with posting permission.
5. `pip install -r requirements.txt`
6. `python main.py`

Do not publish your bot token or commit `.env`.
