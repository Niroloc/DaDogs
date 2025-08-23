from typing import Coroutine, Any

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery

from src.utils.db import Db


class Commander:
    def __init__(self):
        self.db = Db()
        self.main_menu_command_to_callback: dict[str, Any] = {
            'Выгул': self.walk,
            'Добавить собаку': self.add_dog,
            'Удалить собаку': self.delete_dog
        }
        self.steps_in_menu_commands_callback: dict[str, int] = {
            k: 0 for k in self.main_menu_command_to_callback
        }
        self.data_to_callback: dict[str, Any] = {
            "dog_walk": self.dog_walk,
            "all_dogs": self.extend_dogs,
            "dog_dele": self.dog_dele
        }
        self.last_command = 'Выгул'
        self.input_enabled = False

    async def dog_walk(self, callback: CallbackQuery) -> None:
        pass

    async def extend_dogs(self, callback: CallbackQuery) -> None:
        pass

    async def dog_dele(self, callback: CallbackQuery) -> None:
        pass

    def _get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.main_menu_command_to_callback]
        buttons = [buttons[0: 1], buttons[1:]]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    async def walk(self, msg: Message) -> None:
        builder = InlineKeyboardBuilder()
        top_dogs = self.db.get_dogs()
        for ident, name in top_dogs[: 5]:
            builder.add(InlineKeyboardButton(text=name, callback_data=f"dog_walk_{ident}"))
        if len(top_dogs) > 5:
            builder.add(InlineKeyboardButton(text="Остальные", callback_data="all_dogs"))
        await msg.answer(text = "Выгул завершён?", reply_markup=self._get_kb())
        await msg.answer(text="Выберите собаку, с которой погуляли", reply_markup=builder.as_markup())

    async def add_dog(self, msg: Message) -> None:
        if self.steps_in_menu_commands_callback[self.last_command] == 0:
            await msg.answer(text="Введите кличку новой собаки")
        else:
            name = msg.text
            res = self.db.add_dog(name)
            if res == -1:
                await msg.answer(text="Не удалось добавить новую собаку")
            else:
                await msg.answer(text="Собака успешно добавлена")
        self.steps_in_menu_commands_callback[self.last_command] ^= 1

    async def delete_dog(self, msg: Message) -> None:
        builder = InlineKeyboardBuilder()
        top_dogs = self.db.get_dogs()
        for ident, name in top_dogs:
            builder.add(InlineKeyboardButton(text=name, callback_data=f"dog_dele_{ident}"))
        await msg.answer(text="Очень жаль!", reply_markup=self._get_kb())
        await msg.answer(text="Выберите собаку, которую больше не хотите видеть в списках", reply_markup=builder.as_markup())

    def get_main_menu_callback(self, command):
        if command not in self.main_menu_command_to_callback:
            return self.main_menu_command_to_callback[self.last_command]
        for k in self.steps_in_menu_commands_callback:
            self.steps_in_menu_commands_callback[k] = 0
        self.last_command = command
        return self.main_menu_command_to_callback[command]