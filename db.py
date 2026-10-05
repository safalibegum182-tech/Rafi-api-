import aiosqlite
from datetime import datetime,timezone
DB_PATH='data/bot.db'
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript('''
        CREATE TABLE IF NOT EXISTS signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT,pair TEXT NOT NULL,display_pair TEXT NOT NULL,
          side TEXT NOT NULL,score INTEGER NOT NULL,entry_time TEXT NOT NULL,entry_price REAL NOT NULL,
          signal_type TEXT NOT NULL,channel_message_id INTEGER,status TEXT DEFAULT 'PENDING',
          exit_price REAL,result TEXT,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);''')
        await db.commit()
async def get_setting(key,default=None):
    async with aiosqlite.connect(DB_PATH) as db:
        c=await db.execute('SELECT value FROM settings WHERE key=?',(key,)); r=await c.fetchone(); return r[0] if r else default
async def set_setting(key,value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,str(value))); await db.commit()
async def insert_signal(s):
    async with aiosqlite.connect(DB_PATH) as db:
        c=await db.execute('INSERT INTO signals(pair,display_pair,side,score,entry_time,entry_price,signal_type,channel_message_id,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(s['pair'],s['display_pair'],s['side'],s['score'],s['entry_time'],s['entry_price'],s['signal_type'],s.get('channel_message_id'),'PENDING',datetime.now(timezone.utc).isoformat())); await db.commit(); return c.lastrowid
async def update_result(i,exit_price,result):
    async with aiosqlite.connect(DB_PATH) as db: await db.execute('UPDATE signals SET exit_price=?,result=?,status=? WHERE id=?',(exit_price,result,result,i)); await db.commit()
async def daily_auto_count(day):
    async with aiosqlite.connect(DB_PATH) as db:
        c=await db.execute("SELECT COUNT(*) FROM signals WHERE signal_type='AUTO' AND substr(created_at,1,10)=?",(day,)); r=await c.fetchone(); return int(r[0] or 0)
async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        c=await db.execute("SELECT COUNT(*),SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END),SUM(CASE WHEN result='LOSS' THEN 1 ELSE 0 END),SUM(CASE WHEN result='DRAW' THEN 1 ELSE 0 END) FROM signals"); r=await c.fetchone(); return {'total':int(r[0] or 0),'win':int(r[1] or 0),'loss':int(r[2] or 0),'draw':int(r[3] or 0)}
