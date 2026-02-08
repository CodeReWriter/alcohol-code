from aiogram import Router
from aiogram.filters import CommandStart, StateFilter

from . import start
import states
from filters import TextFilter, ChatTypeFilter

# from ... import states


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(
        start.start,
        TextFilter("🏠В главное меню"),  # noqa: RUF001
        StateFilter(states.user.UserMainMenu.menu),
    )

    return user_router
