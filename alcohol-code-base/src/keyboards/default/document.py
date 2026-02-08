from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from typing import List
from enums.sheets import Sheet


class DocumentKeyboards:
    """
    Клавиатуры для работы с документами.
    """

    @staticmethod
    def project_selection(project_names: List[str]) -> ReplyKeyboardMarkup:
        """
        Создает клавиатуру для выбора проекта.

        Args:
            project_names: Список названий проектов

        Returns:
            Клавиатура с кнопками проектов
        """
        try:
            builder = ReplyKeyboardBuilder()

            # Добавляем кнопки проектов (по 2 в ряд)
            for project_name in project_names:
                builder.add(KeyboardButton(text=project_name))

            # Настраиваем расположение кнопок
            builder.adjust(2)  # 2 кнопки проектов в ряд, кнопка отмены отдельно

            # Добавляем кнопку отмены
            builder.row(KeyboardButton(text="🚫 Отмена"))

            return builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Выберите проект...",
            )

        except Exception as e:
            # В случае ошибки возвращаем простую клавиатуру с отменой
            builder = ReplyKeyboardBuilder()
            builder.add(KeyboardButton(text="🚫 Отмена"))
            return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def document_type_selection() -> ReplyKeyboardMarkup:
        """
        Создает клавиатуру для выбора типа документа.

        Returns:
            Клавиатура с типами документов
        """
        try:
            builder = ReplyKeyboardBuilder()

            # Добавляем кнопки типов документов
            builder.add(KeyboardButton(text="📦 Товары"))
            builder.add(KeyboardButton(text="🔧 Услуги"))
            builder.add(KeyboardButton(text="🚫 Отмена"))

            # Настраиваем расположение
            builder.adjust(2, 1)  # 2 кнопки типов в ряд, отмена отдельно

            return builder.as_markup(
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Выберите тип документа...",
            )

        except Exception as e:
            # В случае ошибки возвращаем простую клавиатуру с отменой
            builder = ReplyKeyboardBuilder()
            builder.add(KeyboardButton(text="🚫 Отмена"))
            return builder.as_markup(resize_keyboard=True)
