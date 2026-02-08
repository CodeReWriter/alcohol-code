"""Состояния для административных команд."""

from aiogram.fsm.state import State, StatesGroup


class AddPointStates(StatesGroup):
    """
    Состояния для процесса добавления новой точки и связанной с ней таблицы.
    """
    waiting_for_point_name = State()
    waiting_for_sheet_id = State()
