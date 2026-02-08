
"""Модели для расширенных данных о товарах и услугах с рыночной информацией."""

from typing import Optional
from pydantic import Field, field_validator

from models.document_goods import GoodsDocumentItem
from models.document_jobs import JobsDocumentItem


class GoodsDocumentItemExtended(GoodsDocumentItem):
    """
    Расширенная модель элемента накладной товаров с рыночной информацией.

    Наследует все поля от GoodsDocumentItem и добавляет данные о рыночных ценах
    и анализе, полученные через поиск в интернете.

    Attributes:
        name: Название товара
        quantity: Количество
        unit: Единица измерения
        price: Цена за единицу из документа
        total: Общая стоимость из документа
        average_market_price: Средняя рыночная цена товара (может быть None)
        min_market_price: Минимальная рыночная цена товара (может быть None)
        market_analysis: Краткий анализ рынка с ссылками на источники (может быть None)
    """

    average_market_price: Optional[float] = Field(
        default=None,
        description="Средняя рыночная цена товара",
        ge=0,
    )
    min_market_price: Optional[float] = Field(
        default=None,
        description="Минимальная рыночная цена товара",
        ge=0,
    )
    market_analysis: Optional[str] = Field(
        default=None,
        description="Краткий анализ рынка с ссылками на источники информации",
    )

    @field_validator("average_market_price", "min_market_price", mode="before")
    @classmethod
    def validate_market_prices(cls, v: Optional[float]) -> Optional[float]:
        """
        Валидирует рыночные цены.

        Проверяет, что цена неотрицательная, если она указана.

        Args:
            v: Значение цены для валидации

        Returns:
            Валидированное значение цены или None

        Raises:
            ValueError: Если цена отрицательная
        """
        if v is not None and v < 0:
            raise ValueError("Рыночная цена не может быть отрицательной")
        return v

    @field_validator("market_analysis", mode="before")
    @classmethod
    def validate_market_analysis(cls, v: Optional[str]) -> Optional[str]:
        """
        Валидирует текст анализа рынка.

        Очищает пустые строки и проверяет минимальную длину.

        Args:
            v: Текст анализа для валидации

        Returns:
            Валидированный текст анализа или None
        """
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            # Проверяем минимальную длину осмысленного анализа
            if len(v) < 10:
                return None
        return v


class JobsDocumentItemExtended(JobsDocumentItem):
    """
    Расширенная модель элемента накладной услуг с рыночной информацией.

    Наследует все поля от JobsDocumentItem и добавляет данные о рыночных ценах
    и анализе, полученные через поиск в интернете.

    Attributes:
        name: Название услуги
        quantity: Количество
        unit: Единица измерения
        price: Цена за единицу из документа
        total: Общая стоимость из документа
        average_market_price: Средняя рыночная цена услуги (может быть None)
        min_market_price: Минимальная рыночная цена услуги (может быть None)
        market_analysis: Краткий анализ рынка с ссылками на источники (может быть None)
    """

    average_market_price: Optional[float] = Field(
        default=None,
        description="Средняя рыночная цена услуги",
        ge=0,
    )
    min_market_price: Optional[float] = Field(
        default=None,
        description="Минимальная рыночная цена услуги",
        ge=0,
    )
    market_analysis: Optional[str] = Field(
        default=None,
        description="Краткий анализ рынка с ссылками на источники информации",
    )

    @field_validator("average_market_price", "min_market_price", mode="before")
    @classmethod
    def validate_market_prices(cls, v: Optional[float]) -> Optional[float]:
        """
        Валидирует рыночные цены.

        Проверяет, что цена неотрицательная, если она указана.

        Args:
            v: Значение цены для валидации

        Returns:
            Валидированное значение цены или None

        Raises:
            ValueError: Если цена отрицательная
        """
        if v is not None and v < 0:
            raise ValueError("Рыночная цена не может быть отрицательной")
        return v

    @field_validator("market_analysis", mode="before")
    @classmethod
    def validate_market_analysis(cls, v: Optional[str]) -> Optional[str]:
        """
        Валидирует текст анализа рынка.

        Очищает пустые строки и проверяет минимальную длину.

        Args:
            v: Текст анализа для валидации

        Returns:
            Валидированный текст анализа или None
        """
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            # Проверяем минимальную длину осмысленного анализа
            if len(v) < 10:
                return None
        return v


if __name__ == "__main__":
    # Пример использования для тестирования
    goods_item = GoodsDocumentItemExtended(
        name="Цемент М500",
        quantity=10,
        unit="мешок",
        price=250.0,
        total=2500.0,
        average_market_price=280.0,
        min_market_price=240.0,
        market_analysis="Средняя цена цемента М500 в Украине составляет 280 грн за мешок. "
        "Минимальная цена найдена на сайте budmarket.com.ua - 240 грн. "
        "Источники: budmarket.com.ua, epicentr.ua",
    )
    print("Товар с рыночными данными:")
    print(goods_item.model_dump_json(indent=2, ensure_ascii=False))

    jobs_item = JobsDocumentItemExtended(
        name="Штукатурка стен",
        quantity=50,
        unit="м2",
        price=150.0,
        total=7500.0,
        average_market_price=180.0,
        min_market_price=120.0,
        market_analysis="Средняя стоимость штукатурки стен в Киеве - 180 грн/м2. "
        "Минимальная цена от частных мастеров - 120 грн/м2. "
        "Источники: prom.ua, olx.ua",
    )
    print("\nУслуга с рыночными данными:")
    print(jobs_item.model_dump_json(indent=2, ensure_ascii=False))

    # Тест валидации отрицательных цен
    try:
        invalid_item = GoodsDocumentItemExtended(
            name="Тест",
            quantity=1,
            unit="шт",
            price=100.0,
            total=100.0,
            average_market_price=-50.0,  # Это вызовет ошибку
        )
    except ValueError as e:
        print(f"\nОжидаемая ошибка валидации: {e}")
