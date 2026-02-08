"""Модели для сопоставления имен точек и идентификаторов Google Sheets (файлов данных)."""

from pydantic import BaseModel, Field
from typing import Dict


class PointNameToSheetsIdMapping(BaseModel):
    """
    Модель для хранения сопоставлений имен точек и ID Google таблиц.

    Атрибуты:
        pointname_to_sheetsid (Dict[str, str]): Словарь, где ключ - это имя точки (например, 'template_test'),
                                               а значение - ID Google таблицы.
    """

    pointname_to_sheetsid: Dict[str, str] = Field(
        default_factory=dict,
        description="Словарь сопоставлений 'имя точки' -> 'ID таблицы'",
    )