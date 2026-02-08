from pathlib import Path
from typing import Optional, Tuple, Type, Union
import json

from pydantic import BaseModel, Field, field_validator
from pydantic import PostgresDsn

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)

BASE_DIR = Path(__file__).parent.parent


class LogConfig(BaseModel):
    """Конфигурация логирования."""

    # CRITICAL = 50
    # FATAL = CRITICAL
    # ERROR = 40
    # WARNING = 30
    # WARN = WARNING
    # INFO = 20
    # DEBUG = 10
    # NOTSET = 0
    level: str = "INFO"
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Формат логирования"
    )
    file: Optional[Path] = Field(None, description="Путь к файлу логов")


class TelegramConfig(BaseModel):
    """Конфигурация Telegram бота."""

    bot_token: str = ""
    bot_username: Optional[str] = Field(None, description="Username бота")

    # Webhook настройки (опционально)
    webhook_url: Optional[str] = Field(None, description="URL для webhook")
    webhook_path: str = Field("/webhook", description="Путь для webhook")
    webhook_secret: Optional[str] = Field(None, description="Секрет для webhook")


class N8NConfig(BaseModel):
    """Конфигурация интеграции с n8n."""

    webhook_url: Optional[str] = None
    timeout: int = Field(300, description="Таймаут для запросов к n8n (секунды)")


class GeminiConfig(BaseModel):
    """Конфигурация Google Gemini."""

    api_key: Optional[str] = Field(None, description="API ключ для Google Gemini")
    model: str = Field("gemini-2.5-flash", description="Модель Gemini для анализа")
    # model: str = Field("gemini-2.5-pro", description="Модель Gemini для анализа")
    timeout: int = Field(60, description="Таймаут для запросов к Gemini (секунды)")


class PerplexityConfig(BaseModel):
    """Конфигурация Perplexity API для поиска рыночных цен."""

    api_key: Optional[str] = Field(
        None, 
        description="API ключ для Perplexity"
    )
    model: str = Field(
        "llama-3.1-sonar-small-128k-online",
        description="Модель Perplexity для поиска информации"
    )
    timeout: int = Field(
        30, 
        description="Таймаут для запросов к Perplexity (секунды)"
    )


class GoogleConfig(BaseModel):
    """Конфигурация Google Services."""

    credentials_path: Path = Field(
        Path(BASE_DIR / "credentials.json"),
        description="Путь к файлу с учетными данными Google"
    )
    # ID папки в которой будут сохраняться документы
    drive_folder_id: Optional[str] = Field(
        None,
        description="ID папки Google Drive для сохранения файлов"
    )
    # ID таблицы в Google Sheets
    sheets_template_id: Optional[str] = Field(
        None,
        description="ID шаблона Google Sheets"
    )
    # Email делегирования
    delegated_user_email: Optional[str] = Field(
        None,
        description="Email пользователя для делегирования прав сервисного аккаунта"
    )
    # Альтернативный подход - использование личного аккаунта
    use_personal_account: bool = Field(
        default=False,
        description="Использовать личный аккаунт вместо сервисного"
    )

    @field_validator("credentials_path")
    @classmethod
    def validate_credentials_path(cls, v: Path) -> Path:
        """
        Валидирует путь к файлу учетных данных Google.

        Args:
            v: Путь к файлу.

        Returns:
            Валидный путь к файлу.

        Raises:
            ValueError: Если файл не найден или не является файлом.
        """
        try:
            if not v.exists():
                raise ValueError(f"Файл учетных данных Google не найден по пути: {v}")
            if not v.is_file():
                raise ValueError(f"Путь учетных данных Google не является файлом: {v}")
        except Exception as e:
            # Перехватываем возможные ошибки доступа к файловой системе
            raise ValueError(f"Ошибка при проверке пути к файлу учетных данных: {e}")
        return v

class FilesConfig(BaseModel):
    """Конфигурация работы с файлами."""

    temp_dir: Path = Field(Path("temp"), description="Директория для временных файлов")
    max_file_size: int = Field(50 * 1024 * 1024, description="Максимальный размер файла (байты)")
    allowed_document_extensions: list[str] = Field(
        [".pdf", ".docx", ".doc"],
        description="Разрешенные расширения документов"
    )
    allowed_image_extensions: list[str] = Field(
        [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"],
        description="Разрешенные расширения изображений"
    )

    @field_validator("temp_dir")
    @classmethod
    def validate_temp_dir(cls, v: Path) -> Path:
        """Валидирует и создает директорию для временных файлов."""
        try:
            v.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Не удалось создать директорию для временных файлов: {e}")
        return v

    @field_validator("allowed_document_extensions", "allowed_image_extensions")
    @classmethod
    def validate_extensions(cls, v: list[str]) -> list[str]:
        """Валидирует расширения файлов."""
        return [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in v]


class SecurityConfig(BaseModel):
    """Конфигурация безопасности."""

    admin_user_ids: list[int] = Field(
        default_factory=list,
        description="ID администраторов бота"
    )
    rate_limit_requests: int = Field(10, description="Лимит запросов в минуту")
    rate_limit_window: int = Field(60, description="Окно для лимита запросов (секунды)")

    @field_validator("admin_user_ids", mode="before")
    @classmethod
    def parse_admin_user_ids(cls, v: Union[str, list, None]) -> list[int]:
        """
        Парсит ID администраторов из различных форматов.

        Args:
            v: Значение поля, которое может быть строкой, списком или None.

        Returns:
            Список целочисленных ID администраторов.

        Raises:
            ValueError: Если ID администраторов имеют неверный формат.
        """
        if not v:
            return []

        # Если это уже список
        if isinstance(v, list):
            try:
                return [int(user_id) for user_id in v]
            except (ValueError, TypeError) as e:
                raise ValueError(f"Неверный формат ID администраторов в списке: {v}. {e}")

        # Если это строка
        if isinstance(v, str):
            v = v.strip()

            # Попробуем парсить как JSON
            if v.startswith('[') and v.endswith(']'):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [int(user_id) for user_id in parsed]
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    raise ValueError(f"Неверный JSON формат для admin_user_ids: '{v}'. {e}")

            # Парсим как строку, разделенную запятыми
            try:
                return [int(user_id.strip()) for user_id in v.split(',') if user_id.strip()]
            except ValueError as e:
                raise ValueError(f"Неверный формат ID администраторов в строке: '{v}'. {e}")

        raise ValueError(f"Неподдерживаемый тип для admin_user_ids: {type(v)}")

class ProcessingConfig(BaseModel):
    """Конфигурация обработки документов."""

    max_concurrent_processing: int = Field(3, description="Максимум одновременных обработок")
    processing_timeout: int = Field(600, description="Таймаут обработки документа (секунды)")


class NotificationConfig(BaseModel):
    """Конфигурация уведомлений."""

    chat_id: Optional[int] = Field(
        None,
        description="ID чата для уведомлений об ошибках"
    )
    send_error_notifications: bool = Field(
        False,
        description="Отправлять уведомления об ошибках"
    )


class DevelopmentConfig(BaseModel):
    """Конфигурация режима разработки."""

    debug: bool = Field(False, description="Режим отладки")
    development_mode: bool = Field(False, description="Режим разработки")


# class DBConfig(BaseModel):
#     url: Optional[PostgresDsn] = (
#         "postgresql+asyncpg://postgres:@192.168.3.50:5432/autotrader"
#     )
#
#     echo: bool = False
#     echo_pool: bool = False
#     max_overflow: int = 45
#     pool_size: int = 10
#
#     naming_convention: dict[str, str] = {
#         "ix": "ix_%(column_0_label)s",
#         "uq": "uq_%(table_name)s_%(column_0_N_name)s",
#         "ck": "ck_%(table_name)s_`%(constraint_name)s`",
#         "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#         "pk": "pk_%(table_name)s",
#     }


class Settings(BaseSettings):
    """Основные настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR / "example.env"), str(BASE_DIR / ".env")),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="BOT__",
        extra="ignore",
    )

    telegram: TelegramConfig = TelegramConfig()
    google: GoogleConfig = GoogleConfig()
    gemini: GeminiConfig = GeminiConfig()
    perplexity: PerplexityConfig = PerplexityConfig()
    n8n: N8NConfig = N8NConfig()
    files: FilesConfig = FilesConfig()
    security: SecurityConfig = SecurityConfig()
    processing: ProcessingConfig = ProcessingConfig()
    notifications: NotificationConfig = NotificationConfig()
    development: DevelopmentConfig = DevelopmentConfig()
    # db: DBConfig = DBConfig()
    # rabbitmq: RabbitMQSettings = RabbitMQSettings()
    log: LogConfig = LogConfig()
    log_dir: Path = BASE_DIR / "logs"

    def is_admin(self, user_id: int) -> bool:
        """
        Проверяет, является ли пользователь администратором.

        Args:
            user_id: ID пользователя

        Returns:
            True, если пользователь администратор
        """
        return user_id in self.security.admin_user_ids

    def get_allowed_extensions(self) -> set[str]:
        """
        Возвращает все разрешенные расширения файлов.

        Returns:
            Множество разрешенных расширений
        """
        return set(self.files.allowed_document_extensions + self.files.allowed_image_extensions)

    def is_image_extension(self, extension: str) -> bool:
        """
        Проверяет, является ли расширение изображением.

        Args:
            extension: Расширение файла

        Returns:
            True, если это расширение изображения
        """
        return extension.lower() in self.files.allowed_image_extensions

    def is_document_extension(self, extension: str) -> bool:
        """
        Проверяет, является ли расширение документом.

        Args:
            extension: Расширение файла

        Returns:
            True, если это расширение документа
        """
        return extension.lower() in self.files.allowed_document_extensions

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
            **kwargs
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Переопределяем порядок источников: переменные окружения имеют высший приоритет."""
        return env_settings, dotenv_settings, init_settings, file_secret_settings


settings = Settings()


def get_settings() -> Settings:
    """
    Возвращает экземпляр настроек приложения.

    Returns:
        Настройки приложения
    """
    return settings


if __name__ == "__main__":
    settings = get_settings()
    for k,v in settings.security.model_dump().items():
        print(k,v)
