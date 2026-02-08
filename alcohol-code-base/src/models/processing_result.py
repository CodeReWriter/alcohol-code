from pathlib import Path

from pydantic import BaseModel, Field, ConfigDict

from models.document_analysis import DocumentAnalysis


class ProcessingResult(BaseModel):
    """
    Результат обработки документа.

    Поддерживает как Google сервисы, так и локальное сохранение.
    """

    success: bool = Field(..., description="Успешность обработки")
    analysis: DocumentAnalysis | None = Field(None, description="Результат анализа")
    error_message: str | None = Field(None, description="Сообщение об ошибке")

    # Google сервисы
    google_sheet_url: str | None = Field(None, description="URL Google таблицы")

    # Локальное сохранение
    local_excel_path: Path | None = Field(
        default=None, description="Путь к локальному Excel файлу"
    )
    local_json_path: Path | None = Field(
        default=None, description="Путь к локальному JSON файлу"
    )
    is_local_processing: bool = Field(
        default=False, description="Флаг локальной обработки"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)
