import asyncio
import logging

from config import get_settings
from handlers import start_router, document_router, admin_addpoint_router

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

settings = get_settings()

if settings.development.development_mode:
    TOKEN = settings.telegram.bot_token_test  # Получаем токен бота из настроек
else:
    TOKEN = settings.telegram.bot_token  # Получаем токен бота из настроек

# N8N_WEBHOOK_URL = settings.n8n.webhook_url
# GEMINI_API_KEY = settings.gemini.api_key
#
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")
# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
# if not N8N_WEBHOOK_URL:
#     raise ValueError("N8N_WEBHOOK_URL не найден в переменных окружения")


async def main() -> None:
    """Основная функция запуска бота."""
    try:
        # Dispatcher is a root router
        dp = Dispatcher()
        # Register all the routers from handlers package
        dp.include_routers(
            start_router,
            admin_addpoint_router,  # Добавляем роутер для административной функции
            document_router,  # Добавляем роутер для документов
            # echo_router,
        )

        # Initialize Bot instance with default bot properties
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        # Удаляем webhook перед запуском polling
        await bot.delete_webhook(drop_pending_updates=True)

        # And the run events dispatching
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
