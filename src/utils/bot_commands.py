import logging
import time
from traceback import format_exc
from typing import Coroutine, Any, Callable
from datetime import datetime, date, timedelta, time

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
            'Удалить собаку': self.delete_dog,
            'Детализация по собакам': self.get_amounts_by_dogs,
            'Отчёт по сегодняшним выгулам': self.get_all_walks_today
        }
        self.steps_in_message_callbacks: dict[str, int] = {
            k: 0 for k in self.message_to_callback
        }
        self.alias_to_callback: dict[str, Callable[[CallbackQuery], Coroutine[Any, Any, None]]] = {
            "walker": self.walker,
            "extend": self.extend,
            "delete": self.delete,
            "inputq": self.inputq
        }
        self.last_command: str = 'Выгул'
        self.saved_alias_prefix: str | None = None

    async def walker(self, callback: CallbackQuery) -> None:
        args = self._get_args_from_alias(callback.data)
        if len(args) == 1:
            builder = InlineKeyboardBuilder()
            dates = [date.today() - timedelta(days=i) for i in range(5)]
            for dt in dates:
                builder.row(
                    InlineKeyboardButton(
                        text=dt.strftime("%d-%m"),
                        callback_data=callback.data+"_"+dt.strftime('%Y-%m-%d')
                    )
                )
            await callback.message.edit_text(text="Выберите дату выгула", reply_markup=builder.as_markup())
        elif len(args) == 2:
            builder = InlineKeyboardBuilder()
            times = [time(7 + d // 60, d % 60, 0, 0) for d in range(0, 841, 30)]
            for i in range(0, len(times), 6):
                builder.row(
                    *[
                        InlineKeyboardButton(
                            text=t.strftime("%H:%M"),
                            callback_data=callback.data+"_"+t.strftime("%H:%M:%S")
                        )
                        for t in times[i: i+6]
                    ]
                )
                await callback.message.edit_text(text="А теперь выбираем время", reply_markup=builder.as_markup())
        elif len(args) == 3:
            self.saved_alias_prefix = callback.data
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="500", callback_data=callback.data+"_500"),
                        InlineKeyboardButton(text="550", callback_data=callback.data+"_550"),
                        InlineKeyboardButton(text="600", callback_data=callback.data+"_600")
                        )
            builder.row(InlineKeyboardButton(text="1000", callback_data=callback.data+"_1000"),
                        InlineKeyboardButton(text="1100", callback_data=callback.data+"_1100"),
                        InlineKeyboardButton(text="1200", callback_data=callback.data+"_1200")
                        )
            builder.row(InlineKeyboardButton(text="Ввести своё значение", callback_data="inputq_"+callback.data))
            await callback.message.edit_text(text="Теперь выберите сумму", reply_markup=builder.as_markup())
        elif len(args) == 4:
            args = self._get_args_from_alias(callback.data)
            res = self.db.add_walk(*args)
            if res == -1:
                await callback.message.answer(text="Не получилось, всё по новой", reply_markup=self._get_kb())
                return
            name = self.db.get_dog_name_from_id(args[0])
            if name != "":
                name = f" c собакой по имени {name}"
            await callback.message.answer(text=f"Выгул №{res}{name} успешно добавлен", reply_markup=self._get_kb())
        else:
            logging.error(f"An error occurred while processing alias {callback.data}")
            logging.error(format_exc())
            await callback.message.answer(text="Что-то пошло сильно не так", reply_markup=self._get_kb())

    async def extend(self, callback: CallbackQuery) -> None:
        builder = InlineKeyboardBuilder()
        dogs = self.db.get_dogs()
        for i in range(5):
            builder.row(*[
                InlineKeyboardButton(text=dogs[j][1], callback_data=f"walker_{dogs[j][0]}")
                for j in range(i, len(dogs), 5)
            ])
        await callback.message.edit_text(
            text="Выберите собаку из всех, с которой вы погуляли",
            reply_markup=builder.as_markup()
        )


    async def delete(self, callback: CallbackQuery) -> None:
        alias = callback.data
        args = self._get_args_from_alias(alias)
        if len(args) != 1:
            logging.error(format_exc())
            await callback.message.answer(text="Удалить не удалось", reply_markup=self._get_kb())
            return
        ident = args[0]
        self.db.delete_dog(ident)
        await callback.message.answer("Готово!")

    async def empty(self, callback: CallbackQuery) -> None:
        await callback.message.answer(text="Ничего не произошло!")

    async def inputq(self, callback: CallbackQuery) -> None:
        self.saved_alias_prefix = "_".join(callback.data.split("_")[1: ])
        await callback.message.answer(text="Введите стоимость выгула в рублях", reply_markup=self._get_kb())

    async def finish_walk(self, msg: Message) -> None:
        try:
            val = int(msg.text)
        except ValueError:
            logging.warning(f"Input int can't read int from message '{msg.text}'")
            await msg.answer(text="Ошибка! Введите ещё разок", reply_markup=self._get_kb())
            return
        alias = self.saved_alias_prefix[:6]
        if alias == 'walker':
            args = self._get_args_from_alias(self.saved_alias_prefix) + [val]
            res = self.db.add_walk(*args)
            if res == -1:
                await msg.answer(text="Не получилось, всё по новой", reply_markup=self._get_kb())
                self.saved_alias_prefix = None
                return
            name = self.db.get_dog_name_from_id(args[0])
            if name != "":
                name = f" c собакой по имени {name}"
            await msg.answer(text=f"Выгул №{res}{name} успешно добавлен", reply_markup=self._get_kb())
        self.saved_alias_prefix = None

    def _get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.message_to_callback]
        buttons = [buttons[0: 1]] +  [buttons[i: i + 2] for i in range(1, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    async def get_all_walks_today(self, msg: Message) -> None:
        res = self.db.get_walks()
        ans = ""
        s = 0
        for i, (ts, name, quantity) in enumerate(res):
            ans += f"{i + 1}) {name} в {ts[:-3]} за {quantity} рублей;\n"
            s += quantity
        ans += f"итого: {s} рублей."
        await msg.answer(text=ans, reply_markup=self._get_kb())

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
                await msg.answer(text="Не удалось добавить новую собаку", reply_markup=self._get_kb())
            else:
                await msg.answer(text="Собака успешно добавлена", reply_markup=self._get_kb())
        self.steps_in_message_callbacks[self.last_command] ^= 1

    async def delete_dog(self, msg: Message) -> None:
        builder = InlineKeyboardBuilder()
        dogs = self.db.get_dogs()
        for i in range(5):
            builder.row(*[
                InlineKeyboardButton(text=dogs[j][1], callback_data=f"delete_{dogs[j][0]}")
                for j in range(i, len(dogs), 5)
            ])
        await msg.answer(text="Очень жаль!", reply_markup=self._get_kb())
        await msg.answer(
            text="Выберите собаку, которую больше не хотите видеть в списках",
            reply_markup=builder.as_markup()
        )
    async def get_amounts_by_dogs(self, msg: Message) -> None:
        res = self.db.get_amounts_by_dogs()
        ans = ""
        total_rubles = 0
        total_walks = 0
        for i, (name, s, count) in enumerate(res):
            ans += f"{i + 1}. {name}\t{count} выгулов;\t{s} рублей за всё время.\n"
            total_walks += count
            total_rubles += s
        await msg.answer(text=ans+f"Итого: {total_walks} выгулов и {total_rubles} рублей", reply_markup=self._get_kb())

    def get_message_callback(self, command: str) -> Callable[[Message], Coroutine[Any, Any, None]]:
        if command not in self.message_to_callback and self.saved_alias_prefix is None:
            return self.message_to_callback[self.last_command]
        elif command not in self.message_to_callback and self.saved_alias_prefix is not None:
            return self.finish_walk
        self.saved_alias_prefix = None
        self.steps_in_message_callbacks[command] = 0
        self.last_command = command
        return self.message_to_callback[command]

    def get_callback_callback(self, callback: CallbackQuery) -> Callable[[CallbackQuery], Coroutine[Any, Any, None]]:
        alias = callback.data
        if len(alias) < 6 or alias[: 6] not in self.alias_to_callback:
            logging.warning(f"{alias} is not supported")
            return self.empty
        alias = alias[: 6]
        callback.answer()
        return self.alias_to_callback[alias]

    @staticmethod
    def _get_args_from_alias(alias: str) -> list:
        args = alias.split('_')[1: ]
        res = []
        for arg, f in zip(args,
                     [lambda x: int(x),
                      lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
                      lambda x: datetime.strptime(x, '%H:%M:%S').time(),
                      lambda x: int(x)][: len(args)]):
            try:
                res.append(f(arg))
            except:
                logging.warning(f"Unexpected behaviour while parsing '{alias}'")
                logging.warning(format_exc())
                break
        return res
