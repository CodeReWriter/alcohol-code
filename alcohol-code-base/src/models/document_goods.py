from datetime import date
from typing import List
from pydantic import Field, field_validator

from models.document_analysis import DocumentItem, DocumentAnalysis


class GoodsDocumentItem(DocumentItem):
    """Модель элемента накладной."""

    name: str = Field(default="Уточните название", description="Название товара/услуги")
    quantity: float = Field(..., description="Количество")
    unit: str | None = Field(default="шт", description="Единица измерения")
    price: float = Field(..., description="Цена за единицу")
    total: float = Field(..., description="Общая стоимость")

    @field_validator("unit", mode="before")
    @classmethod
    def handle_none_unit(cls, v):
        """Заменяет None на значение по умолчанию для единицы измерения."""
        return "шт" if v is None else v


class GoodsDocumentAnalysis(DocumentAnalysis):
    """Модель результата анализа документа."""

    document_type: str = Field(default="Товарный чек", description="Тип документа")
    document_number: str | None = Field(None, description="Номер документа")
    date: str | None = Field(
        date.today().strftime("%Y-%m-%d"), description="Дата документа"
    )
    supplier: str | None = Field(None, description="Поставщик")
    customer: str | None = Field(None, description="Покупатель")
    items: List[GoodsDocumentItem] = Field(
        default_factory=list, description="Позиции документа"
    )
    total_amount: float = Field(0.0, description="Общая сумма")
    currency: str | None = Field(default="UAH", description="Валюта")
    confidence: float = Field(0.0, description="Уверенность распознавания")

    @field_validator("currency", mode="before")
    @classmethod
    def handle_none_currency(cls, v):
        """Заменяет None на значение по умолчанию для валюты."""
        return "UAH" if v is None else v


if __name__ == "__main__":
    """Тестирование валидации моделей."""
    try:
        # Тестовые данные с None значениями
        data = {
            "document_type": "Товарный чек",
            "document_number": None,
            "date": "2025-07-18",
            "supplier": "Кавалленко Р.О.",
            "customer": None,
            "items": [
                {
                    "name": "Двигатель 117-60",
                    "quantity": 1,
                    "unit": "шт",
                    "price": 11008.77,
                    "total": 11008.77,
                },
                {
                    "name": "Доставка",
                    "quantity": 1,
                    "unit": None,  # Будет заменено на "шт"
                    "price": 2000.0,
                    "total": 2000.0,
                },
            ],
            "total_amount": 13008.77,
            "currency": None,  # Будет заменено на "UAH"
            "confidence": 0.85,
        }

        # Создаем объект DocumentAnalysis
        analysis = GoodsDocumentAnalysis.model_validate(data)
        print("✅ Валидация прошла успешно!")
        print(f"Валюта: {analysis.currency}")
        print(f"Единица измерения для доставки: {analysis.items[1].unit}")
        print(f"Анализ: {analysis.model_dump()}")

    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")

    data = {
        "document_type": "Товарный чек",
        "document_number": None,
        "date": "2025-07-18",
        "supplier": "Кавалленко Р.О.",
        "customer": None,
        "items": [
            {
                "name": "Двигатель 117-60",
                "quantity": 1,
                "unit": "шт",
                "price": 11008.77,
                "total": 11008.77,
            },
            {
                "name": "Доставка",
                "quantity": 1,
                "unit": None,
                "price": 2000.0,
                "total": 2000.0,
            },
        ],
        "total_amount": 13008.77,
        "currency": None,
        "confidence": 0.85,
    }

    analysis = GoodsDocumentAnalysis.model_validate(data)
    print(analysis)
