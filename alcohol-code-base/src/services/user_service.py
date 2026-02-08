import json
import logging
from pathlib import Path
from typing import Optional, Dict
from threading import RLock

from config import BASE_DIR
from models.user_mapping import UserMapping


class UserService:
    """
    Сервис для управления сопоставлениями ID и имен пользователей Telegram.

    Хранит данные в JSON-файле для обеспечения персистентности без БД.
    Обеспечивает потокобезопасный доступ к файлу.

    Args:
        storage_path: Путь к JSON-файлу для хранения данных.
    """

    def __init__(self, storage_path: Path = None):
        """
        Инициализирует сервис управления пользователями.

        Args:
            storage_path: Путь к файлу хранения.
        """
        self.storage_path = storage_path or Path(
            BASE_DIR / "src/json_data/user_map.json"
        )
        self.logger = logging.getLogger(__name__)
        self._lock = RLock()  # Блокировка для потокобезопасной записи
        self._data: UserMapping = self._load_data()

    def get_all_users(self) -> Dict[str, str]:
        """
        Возвращает словарь всех пользователей (ID -> Username).

        Returns:
            Словарь с сопоставлениями всех пользователей.
        """
        return self._data.id_to_username.copy()

    def get_username(self, user_id: int) -> Optional[str]:
        """
        Получает имя пользователя по его ID.

        Args:
            user_id: ID пользователя Telegram.

        Returns:
            Имя пользователя или None, если не найдено.
        """
        return self._data.id_to_username.get(str(user_id))

    def get_user_id(self, username: str) -> Optional[int]:
        """
        Получает ID пользователя по его имени.

        Args:
            username: Имя пользователя Telegram.

        Returns:
            ID пользователя или None, если не найдено.
        """
        user_id_str = self._data.username_to_id.get(username)
        if user_id_str:
            try:
                return int(user_id_str)
            except (ValueError, TypeError):
                self.logger.error(
                    f"Некорректный ID '{user_id_str}' для пользователя '{username}' в хранилище."
                )
                return None
        return None

    def update_user(self, user_id: int, username: Optional[str]) -> None:
        """
        Добавляет или обновляет информацию о пользователе.

        Если username is None, пользователь будет удален из сопоставлений.

        Args:
            user_id: ID пользователя Telegram.
            username: Имя пользователя Telegram (может быть None).
        """
        user_id_str = str(user_id)

        # Удаляем старые записи, если они есть
        self.remove_user(user_id)

        if username:
            # Добавляем новые записи
            self._data.id_to_username[user_id_str] = username
            self._data.username_to_id[username] = user_id_str
            self.logger.info(
                f"Обновлен пользователь: ID={user_id_str}, Username={username}"
            )

        self._save_data(self._data)

    def remove_user(self, user_id: int) -> None:
        """
        Удаляет пользователя из сопоставлений.

        Args:
            user_id: ID пользователя для удаления.
        """
        user_id_str = str(user_id)

        # Находим старый username по ID
        old_username = self._data.id_to_username.pop(user_id_str, None)

        # Если был старый username, удаляем и обратное сопоставление
        if old_username:
            self._data.username_to_id.pop(old_username, None)
            self.logger.info(
                f"Удален пользователь: ID={user_id_str}, Username={old_username}"
            )
            self._save_data(self._data)

    def _load_data(self) -> UserMapping:
        """
        Загружает данные из JSON-файла.

        Returns:
            Объект UserMapping с данными.
        """
        try:
            with self._lock:
                self.storage_path.parent.mkdir(exist_ok=True, parents=True)
                if self.storage_path.exists() and self.storage_path.stat().st_size > 0:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return UserMapping.model_validate(data)
                else:
                    # Если файл не существует или пуст, создаем пустой
                    initial_data = UserMapping()
                    self._save_data(initial_data)
                    return initial_data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(
                f"Ошибка загрузки файла сопоставления пользователей {self.storage_path}: {e}"
            )
            # В случае ошибки возвращаем пустой объект, чтобы бот продолжил работу
            return UserMapping()
        except Exception as e:
            self.logger.error(
                f"Непредвиденная ошибка при загрузке данных пользователей: {e}"
            )
            return UserMapping()

    def _save_data(self, data: UserMapping) -> None:
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
            self.logger.error(
                f"Ошибка сохранения файла сопоставления пользователей {self.storage_path}: {e}"
            )
        except Exception as e:
            self.logger.error(
                f"Непредвиденная ошибка при сохранении данных пользователей: {e}"
            )


# Создаем единственный экземпляр сервиса для использования в приложении
user_service = UserService()


def get_user_service() -> UserService:
    """
    Возвращает экземпляр сервиса пользователей.

    Returns:
        Экземпляр UserService.
    """
    return user_service


def test_user_service():
    """Тестирование UserService."""
    logging.basicConfig(level=logging.DEBUG)
    print("��� Тестирование UserService...")

    # Используем временный файл для теста
    test_file = Path(BASE_DIR / "src/json_data/test_user_map.json")
    if test_file.exists():
        test_file.unlink()

    service = UserService(storage_path=test_file)
    print("✅ Сервис инициализирован.")

    # 1. Добавление пользователей
    service.update_user(12345, "testuser1")
    service.update_user(67890, "testuser2")
    print("\nДобавлены 2 пользователя.")
    print(f"Все пользователи: {service.get_all_users()}")

    # 2. Поиск
    print("\nТестирование поиска:")
    print(f"Имя для ID 12345: {service.get_username(12345)}")
    print(f"ID для 'testuser2': {service.get_user_id('testuser2')}")

    # 3. Обновление пользователя
    print("\nОбновление пользователя 12345...")
    service.update_user(12345, "testuser1_updated")
    print(f"Новое имя для ID 12345: {service.get_username(12345)}")
    print(f"ID для 'testuser1': {service.get_user_id('testuser1')} (должен быть None)")
    print(f"ID для 'testuser1_updated': {service.get_user_id('testuser1_updated')}")
    print(f"Все пользователи: {service.get_all_users()}")

    # 4. Удаление пользователя
    print("\nУдаление пользователя 67890...")
    service.remove_user(67890)
    print(f"Имя для ID 67890: {service.get_username(67890)} (должен быть None)")
    print(f"Все пользователи: {service.get_all_users()}")

    # 5. Поиск несуществующего пользователя
    print("\nТестирование поиска несуществующего пользователя:")
    print(f"Имя для ID 99999: {service.get_username(99999)}")
    print(f"ID для 'nonexistent': {service.get_user_id('nonexistent')}")

    print(f"Все пользователи: {service.get_all_users()}")

    # 6. Очистка
    if test_file.exists():
        test_file.unlink()
    print(f"\n✅ Тестовый файл {test_file} удален. Тестирование завершено.")


if __name__ == "__main__":
    test_user_service()
