
"""Утилита для обогащения данных о товарах и услугах рыночной информацией."""

import asyncio
import logging
from typing import List, Union

from enums.sheets import Sheet
from models.document_goods import GoodsDocumentItem
from models.document_jobs import JobsDocumentItem
from models.document_items_extended import (
    GoodsDocumentItemExtended,
    JobsDocumentItemExtended,
)
from services.perplexity_service import PerplexityService

logger = logging.getLogger(__name__)


async def extend_items(
    items: List[Union[GoodsDocumentItem, JobsDocumentItem]],
    document_type: Sheet,
    perplexity_service: PerplexityService,
    max_concurrent: int = 2,
) -> List[Union[GoodsDocumentItemExtended, JobsDocumentItemExtended]]:
    """
    Обогащает список товаров или услуг рыночной информацией.

    Для каждого элемента выполняет поиск актуальных рыночных цен через Perplexity API
    и создает расширенную модель с добавлением данных о средней цене, минимальной цене
    и анализе рынка. Запросы выполняются параллельно с ограничением количества
    одновременных операций.

    Args:
        items: Список товаров (GoodsDocumentItem) или услуг (JobsDocumentItem)
        document_type: Тип документа (Sheet.MATERIALS или Sheet.JOBS)
        perplexity_service: Инициализированный сервис Perplexity для поиска цен
        max_concurrent: Максимальное количество одновременных запросов к API (по умолчанию 2)

    Returns:
        Список расширенных моделей (GoodsDocumentItemExtended или JobsDocumentItemExtended)
        с добавленной рыночной информацией. При ошибках поиска рыночные поля заполняются None.

    Raises:
        ValueError: Если document_type не является Sheet.MATERIALS или Sheet.JOBS
        TypeError: Если items содержит элементы неподходящего типа

    Examples:
        >> > perplexity = PerplexityService(api_key="your_key")
        >> > goods = [GoodsDocumentItem(name="Цемент", quantity=10, unit="мешок", price=250, total=2500)]
        >> > extended = await extend_items(goods, Sheet.MATERIALS, perplexity)
        >> > print(extended[0].average_market_price)
        280.0
    """
    if not items:
        logger.info("Список элементов пуст, возвращаем пустой список")
        return []

    if document_type not in [Sheet.MATERIALS, Sheet.JOBS]:
        raise ValueError(
            f"Неподдерживаемый тип документа: {document_type}. "
            f"Ожидается Sheet.MATERIALS или Sheet.JOBS"
        )

    logger.info(
        f"Начало обогащения {len(items)} элементов типа {document_type.value} "
        f"рыночной информацией (макс. {max_concurrent} одновременных запросов)"
    )

    # Семафор для ограничения количества одновременных запросов
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single_item(
        item: Union[GoodsDocumentItem, JobsDocumentItem], index: int
    ) -> Union[GoodsDocumentItemExtended, JobsDocumentItemExtended]:
        """
        Обрабатывает один элемент: получает рыночные данные и создает расширенную модель.

        Args:
            item: Элемент для обработки
            index: Индекс элемента в списке (для логирования)

        Returns:
            Расширенная модель с рыночными данными
        """
        async with semaphore:
            try:
                logger.info(
                    f"[{index + 1}/{len(items)}] Поиск рыночных данных для: "
                    f"{item.name} ({item.unit})"
                )

                # Получаем рыночные данные
                market_data = await perplexity_service.search_market_price(
                    item_name=item.name, item_unit=item.unit or "шт"
                )

                # Извлекаем данные из результата
                average_price = market_data.get("average_price")
                min_price = market_data.get("min_price")
                analysis = market_data.get("analysis", "")

                # Создаем расширенную модель в зависимости от типа документа
                if document_type == Sheet.MATERIALS:
                    extended_item = GoodsDocumentItemExtended(
                        name=item.name,
                        quantity=item.quantity,
                        unit=item.unit,
                        price=item.price,
                        total=item.total,
                        average_market_price=average_price,
                        min_market_price=min_price,
                        market_analysis=analysis if analysis else None,
                    )
                else:  # Sheet.JOBS
                    extended_item = JobsDocumentItemExtended(
                        name=item.name,
                        quantity=item.quantity,
                        unit=item.unit,
                        price=item.price,
                        total=item.total,
                        average_market_price=average_price,
                        min_market_price=min_price,
                        market_analysis=analysis if analysis else None,
                    )

                logger.info(
                    f"[{index + 1}/{len(items)}] Успешно обработан: {item.name} "
                    f"(средняя цена: {average_price}, мин. цена: {min_price})"
                )

                return extended_item

            except Exception as ex:
                logger.error(
                    f"[{index + 1}/{len(items)}] Ошибка при обработке '{item.name}': {ex}",
                    exc_info=True,
                )

                # Создаем расширенную модель без рыночных данных
                try:
                    if document_type == Sheet.MATERIALS:
                        extended_item = GoodsDocumentItemExtended(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            price=item.price,
                            total=item.total,
                            average_market_price=None,
                            min_market_price=None,
                            market_analysis=None,
                        )
                    else:  # Sheet.JOBS
                        extended_item = JobsDocumentItemExtended(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            price=item.price,
                            total=item.total,
                            average_market_price=None,
                            min_market_price=None,
                            market_analysis=None,
                        )

                    logger.warning(
                        f"[{index + 1}/{len(items)}] Создан элемент без рыночных данных: {item.name}"
                    )

                    return extended_item

                except Exception as creation_error:
                    logger.critical(
                        f"[{index + 1}/{len(items)}] Критическая ошибка при создании "
                        f"расширенной модели для '{item.name}': {creation_error}",
                        exc_info=True,
                    )
                    raise

    # Создаем задачи для всех элементов
    tasks = [process_single_item(item, idx) for idx, item in enumerate(items)]

    # Выполняем все задачи параллельно с ограничением
    try:
        extended_items = await asyncio.gather(*tasks, return_exceptions=False)

        success_count = sum(
            1
            for item in extended_items
            if item.average_market_price is not None or item.min_market_price is not None
        )

        logger.info(
            f"Обогащение завершено: {len(extended_items)} элементов обработано, "
            f"{success_count} с рыночными данными, "
            f"{len(extended_items) - success_count} без рыночных данных"
        )

        return extended_items

    except Exception as e:
        logger.error(f"Критическая ошибка при обогащении элементов: {e}", exc_info=True)
        raise


async def extend_single_item(
    item: Union[GoodsDocumentItem, JobsDocumentItem],
    document_type: Sheet,
    perplexity_service: PerplexityService,
) -> Union[GoodsDocumentItemExtended, JobsDocumentItemExtended]:
    """
    Обогащает один товар или услугу рыночной информацией.

    Удобная функция-обертка для обработки одного элемента без необходимости
    создавать список и использовать extend_items.

    Args:
        item: Товар (GoodsDocumentItem) или услуга (JobsDocumentItem)
        document_type: Тип документа (Sheet.MATERIALS или Sheet.JOBS)
        perplexity_service: Инициализированный сервис Perplexity для поиска цен

    Returns:
        Расширенная модель (GoodsDocumentItemExtended или JobsDocumentItemExtended)
        с добавленной рыночной информацией

    Raises:
        ValueError: Если document_type не является Sheet.MATERIALS или Sheet.JOBS
        TypeError: Если item имеет неподходящий тип

    Examples:
        >> > perplexity = PerplexityService(api_key="your_key")
        >> > item = GoodsDocumentItem(name="Цемент", quantity=10, unit="мешок", price=250, total=2500)
        >> > extended = await extend_single_item(item, Sheet.MATERIALS, perplexity)
        >> > print(extended.market_analysis)
        'Средняя цена цемента М500 в Украине...'
    """
    logger.info(f"Обогащение одного элемента: {item.name}")

    result = await extend_items(
        items=[item], document_type=document_type, perplexity_service=perplexity_service
    )

    return result[0]


if __name__ == "__main__":
    # Пример использования для тестирования

    async def test_extend_items():
        """Тестовая функция для проверки работы утилиты обогащения."""
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Замените на ваш реальный API ключ
        api_key = "your_api_key_here"

        try:
            # Инициализация сервиса
            perplexity = PerplexityService(api_key=api_key)

            # Тестовые данные - товары
            goods_items = [
                GoodsDocumentItem(
                    name="Цемент М500",
                    quantity=10,
                    unit="мешок",
                    price=250.0,
                    total=2500.0,
                ),
                GoodsDocumentItem(
                    name="Кирпич красный",
                    quantity=1000,
                    unit="шт",
                    price=5.0,
                    total=5000.0,
                ),
                GoodsDocumentItem(
                    name="Песок речной",
                    quantity=5,
                    unit="тонна",
                    price=300.0,
                    total=1500.0,
                ),
            ]

            print("=" * 80)
            print("ТЕСТ 1: Обогащение списка товаров")
            print("=" * 80)

            extended_goods = await extend_items(
                items=goods_items,
                document_type=Sheet.MATERIALS,
                perplexity_service=perplexity,
                max_concurrent=2,
            )

            print("\nРезультаты для товаров:")
            for idx, item in enumerate(extended_goods, 1):
                print(f"\n{idx}. {item.name}")
                print(f"   Цена из документа: {item.price} грн/{item.unit}")
                print(f"   Средняя рыночная: {item.average_market_price} грн/{item.unit}")
                print(f"   Минимальная рыночная: {item.min_market_price} грн/{item.unit}")
                print(f"   Анализ: {item.market_analysis[:100] if item.market_analysis else 'Нет данных'}...")

            # Тестовые данные - услуги
            jobs_items = [
                JobsDocumentItem(
                    name="Штукатурка стен",
                    quantity=50,
                    unit="м2",
                    price=150.0,
                    total=7500.0,
                ),
                JobsDocumentItem(
                    name="Укладка плитки",
                    quantity=30,
                    unit="м2",
                    price=200.0,
                    total=6000.0,
                ),
            ]

            print("\n" + "=" * 80)
            print("ТЕСТ 2: Обогащение списка услуг")
            print("=" * 80)

            extended_jobs = await extend_items(
                items=jobs_items,
                document_type=Sheet.JOBS,
                perplexity_service=perplexity,
                max_concurrent=2,
            )

            print("\nРезультаты для услуг:")
            for idx, item in enumerate(extended_jobs, 1):
                print(f"\n{idx}. {item.name}")
                print(f"   Цена из документа: {item.price} грн/{item.unit}")
                print(f"   Средняя рыночная: {item.average_market_price} грн/{item.unit}")
                print(f"   Минимальная рыночная: {item.min_market_price} грн/{item.unit}")
                print(f"   Анализ: {item.market_analysis[:100] if item.market_analysis else 'Нет данных'}...")

            # Тест одиночного элемента
            print("\n" + "=" * 80)
            print("ТЕСТ 3: Обогащение одного элемента")
            print("=" * 80)

            single_item = GoodsDocumentItem(
                name="Гипсокартон",
                quantity=20,
                unit="лист",
                price=120.0,
                total=2400.0,
            )

            extended_single = await extend_single_item(
                item=single_item,
                document_type=Sheet.MATERIALS,
                perplexity_service=perplexity,
            )

            print(f"\nРезультат для одного элемента:")
            print(f"   Название: {extended_single.name}")
            print(f"   Цена из документа: {extended_single.price} грн/{extended_single.unit}")
            print(f"   Средняя рыночная: {extended_single.average_market_price} грн/{extended_single.unit}")
            print(f"   Минимальная рыночная: {extended_single.min_market_price} грн/{extended_single.unit}")
            print(f"   Анализ: {extended_single.market_analysis[:100] if extended_single.market_analysis else 'Нет данных'}...")

        except Exception as e:
            logger.error(f"Ошибка в тестовой функции: {e}", exc_info=True)

    # Запуск тестов
    asyncio.run(test_extend_items())
