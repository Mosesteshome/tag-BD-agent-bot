"""Test the tag-BD bot's token and DB connections. Run: bash start_bot.sh check"""
import asyncio
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from telegram import Bot

DB_CHECKS = {
    "DATABASE_URL": "SELECT COUNT(*) FROM restaurants",
    "SQL_DATABASE_URL": "SELECT (SELECT COUNT(*) FROM user_info), (SELECT COUNT(*) FROM bd_replies)",
}


async def check_token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN: not set")
        return
    try:
        async with Bot(token) as bot:
            me = await bot.get_me()
        print(f"TELEGRAM_BOT_TOKEN: OK (@{me.username})")
    except Exception as e:
        print(f"TELEGRAM_BOT_TOKEN: FAILED {e}")


async def check_db(var, sql):
    url = os.environ.get(var)
    if not url:
        print(f"{var}: not set")
        return
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            row = (await conn.execute(text(sql))).fetchone()
        print(f"{var}: OK {tuple(row)}")
    except Exception as e:
        print(f"{var}: FAILED {e}")
    finally:
        await engine.dispose()


async def main():
    await check_token()
    for var, sql in DB_CHECKS.items():
        await check_db(var, sql)


asyncio.run(main())
