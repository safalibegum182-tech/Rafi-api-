import asyncio
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.bot import router,auto_loop
from app import db
from app.config import settings
async def main():
    if not settings.bot_token:raise SystemExit('BOT_TOKEN is missing. Copy .env.example to .env and set it.')
    await db.init_db();bot=Bot(settings.bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML));dp=Dispatcher();dp.include_router(router);scanner=asyncio.create_task(auto_loop(bot))
    try:await dp.start_polling(bot)
    finally:scanner.cancel();await bot.session.close()
if __name__=='__main__':asyncio.run(main())
