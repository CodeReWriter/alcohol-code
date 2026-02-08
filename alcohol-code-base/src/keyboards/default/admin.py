"""Клавиатуры для административных функций."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class AdminButtons:
    """Класс для создания административных клавиатур."""

    @staticmethod
    def sheet_id_input_menu() -> ReplyKeyboardMarkup:
        """
        Клавиатура для этапа ввода ID таблицы.

        Предоставляет опции для изменения имени точки или отмены операции.

        Returns:
            Объект ReplyKeyboardMarkup.
        """
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="✍️ Изменить имя точки"),
            KeyboardButton(text="❌ Отмена")
        )
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def cancel_menu() -> ReplyKeyboardMarkup:
        """
        Клавиатура с единственной кнопкой "Отмена".

        Returns:
            Объект ReplyKeyboardMarkup.
        """
        builder = ReplyKeyboardBuilder()
        builder.row(KeyboardButton(text="❌ Отмена"))
        return builder.as_markup(resize_keyboard=True)