import logging
from traceback import format_exc
from typing import Coroutine, Any, Callable
from datetime import datetime, date

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery

from src.utils.db import Db


class Commander:
    def __init__(self):
        self.db = Db()
        self.message_to_callback: dict[str, Callable[[Message], Coroutine[Any, Any, None]]] = {
            'Выгул': self.walk,
            'Добавить собаку': self.add_dog,
            'Удалить собаку': self.delete_dog
        }
        self.steps_in_message_callbacks: dict[str, int] = {
            k: 0 for k in self.message_to_callback
        }
        self.alias_to_callback: dict[str, Callable[[CallbackQuery], Coroutine[Any, Any, None]]] = {
            "walker": self.walker,
            "extend": self.extend,
            "delete": self.delete
        }
        self.last_command = 'Выгул'
        self.input_enabled = False

    async def walker(self, callback: CallbackQuery) -> None:
        pass

    async def extend(self, callback: CallbackQuery) -> None:
        pass

    async def delete(self, callback: CallbackQuery) -> None:
        alias = callback.data
        args = self._get_args_from_alias(alias)
        if len(args) != 1:
            logging.error(format_exc())
        ident = args[0]
        self.db.delete_dog(ident)
        await callback.message.answer("Готово!")

    async def empty(self, callback: CallbackQuery) -> None:
        pass

    def _get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.message_to_callback]
        buttons = [buttons[0: 1], buttons[1:]]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    async def walk(self, msg: Message) -> None:
        builder = InlineKeyboardBuilder()
        top_dogs = self.db.get_dogs()
        for ident, name in top_dogs[: 5]:
            builder.row(InlineKeyboardButton(text=name, callback_data=f"walker_{ident}"))
        if len(top_dogs) > 5:
            builder.row(InlineKeyboardButton(text="Остальные", callback_data="extend"))
        await msg.answer(text = "Выгул завершён?", reply_markup=self._get_kb())
        await msg.answer(text="Выберите собаку, с которой погуляли", reply_markup=builder.as_markup())

    async def add_dog(self, msg: Message) -> None:
        if self.steps_in_message_callbacks[self.last_command] == 0:
            await msg.answer(text="Введите кличку новой собаки")
        else:
            name = msg.text
            res = self.db.add_dog(name)
            if res == -1:
                await msg.answer(text="Не удалось добавить новую собаку")
            else:
                await msg.answer(text="Собака успешно добавлена")
        self.steps_in_message_callbacks[self.last_command] ^= 1

    async def delete_dog(self, msg: Message) -> None:
        builder = InlineKeyboardBuilder()
        top_dogs = self.db.get_dogs()
        for ident, name in top_dogs:
            builder.add(InlineKeyboardButton(text=name, callback_data=f"delete_{ident}"))
        await msg.answer(text="Очень жаль!", reply_markup=self._get_kb())
        await msg.answer(
            text="Выберите собаку, которую больше не хотите видеть в списках",
            reply_markup=builder.as_markup()
        )

    def get_message_callback(self, command: str) -> Callable[[Message], Coroutine[Any, Any, None]]:
        if command not in self.message_to_callback:
            return self.message_to_callback[self.last_command]
        self.steps_in_message_callbacks[command] = 0
        self.last_command = command
        return self.message_to_callback[command]

    def get_callback_callback(self, callback: CallbackQuery) -> Callable[[CallbackQuery], Coroutine[Any, Any, None]]:
        alias = callback.data
        if len(alias) < 6 or alias[: 6] not in self.alias_to_callback:
            logging.warning(f"{alias} is not supported")
            callback.answer(text="Произошла непредвиденная ошибка:(")
            return self.empty
        alias = alias[: 6]
        return self.alias_to_callback[alias]

    @staticmethod
    def _get_args_from_alias(alias: str) -> list:
        args = alias.split('_')[1: ]
        res = []
        for arg, f in zip(args,
                     [lambda x: int(x),
                      lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
                      lambda x: datetime.strptime(x, '%H:%M:%S').time(),
                      lambda x: int(x)]):
            try:
                res.append(f(arg))
            except:
                logging.warning(f"Unexpected behaviour while parsing '{alias}'")
                logging.warning(format_exc())
                break
        return res
