from datetime import date
from typing import List
from pydantic import BaseModel, Field, field_validator


class DocumentItem(BaseModel):
    """Модель элемента накладной."""

    name: str = Field(description="Название товара/услуги")
    quantity: float = Field(description="Количество")
    unit: str | None = Field(description="Единица измерения")
    price: float = Field(description="Цена за единицу")
    total: float = Field(description="Общая стоимость")
    #
    # @field_validator("unit", mode="before")
    # @classmethod
    # def handle_none_unit(cls, v):
    #     """Заменяет None на значение по умолчанию для единицы измерения."""
    #     return "шт" if v is None else v


class DocumentAnalysis(BaseModel):
    """Модель результата анализа документа."""

    document_type: str = Field(description="Тип документа")
    document_number: str | None = Field(description="Номер документа")
    date: str | None = Field(description="Дата документа")
    supplier: str | None = Field(description="Поставщик / Исполнитель")
    customer: str | None = Field(description="Покупатель / Заказчик")
    items: List[DocumentItem] = Field(
        default_factory=list, description="Позиции документа"
    )
    total_amount: float = Field(0.0, description="Общая сумма")
    currency: str | None = Field(default="UAH", description="Валюта")
    confidence: float = Field(description="Уверенность распознавания")
    #
    # @field_validator("currency", mode="before")
    # @classmethod
    # def handle_none_currency(cls, v):
    #     """Заменяет None на значение по умолчанию для валюты."""
    #     return "UAH" if v is None else v
