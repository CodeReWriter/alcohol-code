
"""Фильтр для проверки прав администратора."""

from aiogram.filters import Filter
from aiogram.types import Message
from config import get_settings


class AdminFilter(Filter):
    """
    Фильтр, который проверяет, является ли пользователь администратором.

    ID администраторов берутся из конфигурации.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Выполняет проверку.

        Args:
            message: Сообщение от пользователя.

        Returns:
            True, если пользователь является администратором, иначе False.
        """
        settings = get_settings()
        user_id = message.from_user.id
        return settings.is_admin(user_id)
