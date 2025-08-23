import asyncio
import logging

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from utils.db import Db
from config.constants import BOT_TOKEN


class DaDogsBot:
    def __init__(self):
        self.db = Db()
        self.dp = Dispatcher()
        self.bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message) -> None:
            await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

        @self.dp.message()
        async def echo_handler(message: Message) -> None:
            try:
                await message.send_copy(chat_id=message.chat.id)
            except TypeError:
                await message.answer("Nice try!")

    def run(self):
        asyncio.run(self.dp.start_polling(self.bot))
    