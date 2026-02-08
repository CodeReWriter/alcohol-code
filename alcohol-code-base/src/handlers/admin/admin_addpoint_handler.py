"""Обработчики административных команд для управления настройками."""

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import get_settings
from filters.admin_filter import AdminFilter
from keyboards.default.admin import AdminButtons
from keyboards.default.basic import BasicButtons
from services.google_service import GoogleService
from services.sheets_mapping_service import SheetsMappingService
from states.admin_states import AddPointStates

logger = logging.getLogger(__name__)
admin_addpoint_router = Router()
admin_addpoint_router.message.filter(AdminFilter())


@admin_addpoint_router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    """
    Обработчик для отмены любого административного действия.
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info(f"Пользователь {message.from_user.id} отменил действие в состоянии {current_state}.")
    await state.clear()
    await message.answer(
        "Действие отменено.",
        reply_markup=BasicButtons.main_menu()
    )


@admin_addpoint_router.message(F.text == "&addpoint")
async def cmd_add_point(message: Message, state: FSMContext):
    """
    Начало процесса добавления новой точки. Запрашивает имя точки.
    """
    await state.set_state(AddPointStates.waiting_for_point_name)
    await message.answer(
        "Введите имя для новой точки (например, 'склад_1' или 'объект_альфа').",
        reply_markup=AdminButtons.cancel_menu()
    )


@admin_addpoint_router.message(AddPointStates.waiting_for_point_name, F.text != "❌ Отмена")
async def process_point_name(message: Message, state: FSMContext):
    """
    Обрабатывает введенное имя точки и запрашивает ID таблицы.
    """
    point_name = message.text.strip()
    await state.update_data(point_name=point_name)
    await state.set_state(AddPointStates.waiting_for_sheet_id)
    await message.answer(
        f"Отлично, имя точки: <b>{point_name}</b>.\n\n"
        "Теперь отправьте ID Google таблицы для отчетов.",
        reply_markup=AdminButtons.sheet_id_input_menu()
    )


@admin_addpoint_router.message(F.text == "✍️ Изменить имя точки", AddPointStates.waiting_for_sheet_id)
async def change_point_name_request(message: Message, state: FSMContext):
    """
    Позволяет вернуться к шагу ввода имени точки.
    """
    await state.set_state(AddPointStates.waiting_for_point_name)
    await message.answer(
        "Введите новое имя для точки.",
        reply_markup=AdminButtons.cancel_menu()
    )


@admin_addpoint_router.message(AddPointStates.waiting_for_sheet_id, F.text)
async def process_sheet_id(message: Message, state: FSMContext):
    """
    Обрабатывает ID таблицы, проверяет права и сохраняет сопоставление.

    """
    sheet_id = message.text.strip()
    # Показываем, что началась проверка
    await message.answer("Проверяю доступ к таблице...")

    settings = get_settings()
    google_service = GoogleService(settings.google.credentials_path)

    has_permissions = await google_service.check_sheet_write_permissions(sheet_id)

    if not has_permissions:
        await message.answer(
            "❌ <b>Ошибка доступа!</b>\n\n"
            "Не удалось получить права на запись в таблицу с указанным ID. "
            "Убедитесь, что:\n"
            "1. ID таблицы скопирован верно.\n"
            f"2. Вы предоставили доступ на редактирование для сервисного аккаунта: "
            f"`\n\n{google_service.get_service_account_email()}`\n\n"
            "Пожалуйста, проверьте и отправьте ID еще раз или отмените операцию.",
            reply_markup=AdminButtons.cancel_menu(),
        )
        return

    data = await state.get_data()
    point_name = data.get("point_name")

    if not point_name:
        await message.answer(
            "Произошла внутренняя ошибка: не найдено имя точки. "
            "Пожалуйста, начните заново с команды `&addpoint`."
        )
        await state.clear()
        return

    # Сохраняем сопоставление
    mapping_service = SheetsMappingService()
    mapping_service.add_or_update_mapping(point_name, sheet_id)

    await message.answer(
        f"✅ <b>Успешно!</b>\n\n"
        f"Точка '<b>{point_name}</b>' успешно связана с таблицей.\n"
        f"ID таблицы: `{sheet_id}`",
        reply_markup=BasicButtons.main_menu(),
    )
    await state.clear()