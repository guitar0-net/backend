# SPDX-FileCopyrightText: 2026 Andrey Kotlyar <guitar0.app@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers import common

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(common.router)

    print("Bot had started to work!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
