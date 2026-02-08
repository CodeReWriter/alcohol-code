"""Сервис для управления сопоставлениями имен точек и ID Google Sheets."""

import json
import logging
from pathlib import Path
from threading import RLock
from typing import Dict, Optional

from common.singleton import Singleton
from config import BASE_DIR
from models.sheets_mapping import PointNameToSheetsIdMapping


class SheetsMappingService(Singleton):
    """
    Сервис для управления данными из файла pointname_sheetsid.json.

    Обеспечивает потокобезопасный доступ к файлу и предоставляет
    методы для CRUD-операций (создание, чтение, обновление, удаление).

    Args:
        storage_path (Path, optional): Путь к JSON-файлу для хранения данных.
                                       По умолчанию 'src/json_data/pointname_sheetsid.json'.
    """

    def __init__(self):
        """
        Инициализирует сервис.

        """
        self.storage_path = Path(BASE_DIR / "src/json_data/pointname_sheetsid.json")
        self.logger = logging.getLogger(__name__)
        self._lock = RLock()  # Блокировка для потокобезопасного доступа к файлу
        self._data: PointNameToSheetsIdMapping = self._load_data()

    def get_sheet_id(self, point_name: str) -> Optional[str]:
        """
        Получает ID таблицы по имени точки.

        Args:
            point_name: Имя точки для поиска.

        Returns:
            ID Google таблицы или None, если имя не найдено.
        """
        return self._data.pointname_to_sheetsid.get(point_name)

    def get_all_mappings(self) -> Dict[str, str]:
        """
        Возвращает все сопоставления.

        Returns:
            Копия словаря со всеми сопоставлениями.
        """
        self.logger.info(f"Сопоставления: {self._data.pointname_to_sheetsid}")
        return self._data.pointname_to_sheetsid.copy()

    def add_or_update_mapping(self, point_name: str, sheet_id: str) -> None:
        """
        Добавляет новое или обновляет существующее сопоставление.

        Args:
            point_name: Имя точки (ключ).
            sheet_id: ID Google таблицы (значение).
        """
        try:
            self.logger.info(f"Таблица \"Имя точки :: ID таблицы\" до добавления/обновления: {point_name} :: {sheet_id}\"")
            self._data.pointname_to_sheetsid[point_name] = sheet_id
            self._save_data(self._data)
            self.logger.info(f"Сопоставление для '{point_name}' добавлено/обновлено.")
            self.logger.info(f"Таблица \"Имя точки :: ID таблицы\" ПОСЛЕ добавления/обновления: {self._data.pointname_to_sheetsid}\"")
        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении/обновлении сопоставления для '{point_name}': {e}"
            )

    def remove_mapping(self, point_name: str) -> bool:
        """
        Удаляет сопоставление по имени точки.

        Args:
            point_name: Имя точки для удаления.

        Returns:
            True, если удаление прошло успешно, иначе False.
        """
        try:
            if point_name in self._data.pointname_to_sheetsid:
                del self._data.pointname_to_sheetsid[point_name]
                self._save_data(self._data)
                self.logger.info(f"Сопоставление для '{point_name}' удалено.")
                return True
            else:
                self.logger.warning(
                    f"Попытка удалить несуществующее сопоставление: '{point_name}'"
                )
                return False
        except Exception as e:
            self.logger.error(
                f"Ошибка при удалении сопоставления для '{point_name}': {e}"
            )
            return False

    def _load_data(self) -> PointNameToSheetsIdMapping:
        """
        Загружает данные из JSON-файла.

        Если файл не существует или пуст, создает новый с пустой структурой.

        Returns:
            Объект PointNameToSheetsIdMapping с загруженными данными.
        """
        try:
            with self._lock:
                self.storage_path.parent.mkdir(exist_ok=True, parents=True)
                if self.storage_path.exists() and self.storage_path.stat().st_size > 0:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return PointNameToSheetsIdMapping.model_validate(data)
                else:
                    # Если файл пуст или не существует, создаем и сохраняем пустую модель
                    initial_data = PointNameToSheetsIdMapping()
                    self._save_data(initial_data)
                    return initial_data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Ошибка загрузки файла {self.storage_path}: {e}")
            return PointNameToSheetsIdMapping()  # Возвращаем пустую модель при ошибке
        except Exception as e:
            self.logger.error(
                f"Непредвиденная ошибка при загрузке {self.storage_path}: {e}"
            )
            return PointNameToSheetsIdMapping()

    def _save_data(self, data: PointNameToSheetsIdMapping) -> None:
        """
        Сохраняет данные в JSON-файл.

        Args:
            data: Данные для сохранения.
        """
        try:
            with self._lock:
                self.storage_path.parent.mkdir(exist_ok=True, parents=True)
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump(data.model_dump(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            self.logger.error(f"Ошибка сохранения файла {self.storage_path}: {e}")
        except Exception as e:
            self.logger.error(f"Непредвиденная ошибка при сохранении данных: {e}")
