import aiogram.types

from .consts import DefaultConstructor


class BasicButtons(DefaultConstructor):
    @staticmethod
    def main_menu() -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает главное меню бота.

        Returns:
            Клавиатура с основными командами
        """
        schema = [2, 2]
        btns = ["📄 Анализ документа", "ℹ️ Помощь", "📊 История", "⚙️ Настройки"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back() -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку возврата в главное меню.

        Returns:
            Клавиатура с кнопкой "Назад"
        """
        schema = [1]
        btns = ["◀️Назад"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def cancel() -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку отмены операции.

        Returns:
            Клавиатура с кнопкой отмены
        """
        schema = [1]
        btns = ["🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel() -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопки возврата и отмены.

        Returns:
            Клавиатура с кнопками "Назад" и "Отмена"
        """
        schema = [1, 1]
        btns = ["◀️Назад", "🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def document_menu() -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает меню для работы с документами.

        Returns:
            Клавиатура с опциями документов
        """
        schema = [1, 2]
        btns = ["📄 Загрузить документ", "◀️Назад", "🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку подтверждения с опциональными кнопками.

        Args:
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопкой подтверждения
        """
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        schema.append(1)
        btns.append("✅Подтвердить")
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def skip(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку пропуска с опциональными кнопками.

        Args:
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопкой пропуска
        """
        schema = [1]
        btns = ["▶️Пропустить"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку "Да" с опциональными кнопками.

        Args:
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопкой "Да"
        """
        schema = [1]
        btns = ["✅Да"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def no(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку "Нет" с опциональными кнопками.

        Args:
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопкой "Нет"
        """
        schema = [1]
        btns = ["❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(
        *,
        add_back: bool = False,
        add_cancel: bool = False,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопки "Да" и "Нет" с опциональными кнопками.

        Args:
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопками "Да" и "Нет"
        """
        schema = [2]
        btns = ["✅Да", "❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def ask_for_users(  # noqa: PLR0913
        text: str,
        *,
        request_id: int = 1,
        user_is_bot: bool | None = False,
        user_is_premium: bool | None = None,
        max_quantity: int | None = 1,
        request_name: bool | None = True,
        request_username: bool | None = True,
        request_photo: bool | None = True,
        add_back: bool = False,
        add_cancel: bool = True,
    ) -> aiogram.types.ReplyKeyboardMarkup:
        """
        Создает кнопку для запроса пользователей.

        Args:
            text: Текст кнопки
            request_id: ID запроса
            user_is_bot: Фильтр по ботам
            user_is_premium: Фильтр по премиум пользователям
            max_quantity: Максимальное количество пользователей
            request_name: Запрашивать имя
            request_username: Запрашивать username
            request_photo: Запрашивать фото
            add_back: Добавить кнопку "Назад"
            add_cancel: Добавить кнопку "Отмена"

        Returns:
            Клавиатура с кнопкой запроса пользователей
        """
        schema = [1]
        btns: list[str | dict[str, str | aiogram.types.KeyboardButtonRequestUsers]] = [
            {
                "text": text,
                "request_users": aiogram.types.KeyboardButtonRequestUsers(
                    request_id=request_id,
                    user_is_bot=user_is_bot,
                    user_is_premium=user_is_premium,
                    max_quantity=max_quantity,
                    request_name=request_name,
                    request_username=request_username,
                    request_photo=request_photo,
                ),
            },
        ]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)  # type: ignore[arg-type]
