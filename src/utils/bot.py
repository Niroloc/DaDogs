import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.config.constants import BOT_TOKEN
from src.utils.bot_commands import Commander
from src.config.constants import ADMIN_ID


class DaDogsBot:
    def __init__(self):
        self.cmdr = Commander()
        self.dp = Dispatcher()
        self.bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message) -> None:
            if not self.check_rights(message):
                return
            await self.cmdr.get_main_menu_callback("")(message)

        @self.dp.message()
        async def echo_handler(message: Message) -> None:
            if not self.check_rights(message):
                return
            await self.cmdr.get_main_menu_callback(message.text)(message)

    def check_rights(self, msg: Message) -> bool:
        return msg.chat.id == ADMIN_ID

    def run(self):
        asyncio.run(self.dp.start_polling(self.bot))
    