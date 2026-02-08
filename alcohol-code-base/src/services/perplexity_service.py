
"""Сервис для работы с Perplexity API для поиска рыночных цен."""

import logging
from typing import Optional, Dict, Any

import aiohttp


class PerplexityService:
    """
    Сервис для поиска рыночных цен товаров и услуг через Perplexity API.
    
    Использует Perplexity API для получения актуальной информации о ценах
    на товары и услуги в Украине с указанием источников.
    
    Attributes:
        api_key: API ключ для Perplexity
        model: Название модели Perplexity
        timeout: Таймаут для HTTP запросов
        api_url: URL эндпоинта Perplexity API
        logger: Логгер для записи событий
    """

    API_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-sonar-small-128k-online",
        timeout: int = 30,
    ):
        """
        Инициализация сервиса Perplexity.

        Args:
            api_key: API ключ для Perplexity
            model: Название модели Perplexity для использования
            timeout: Таймаут для HTTP запросов в секундах

        Raises:
            ValueError: Если api_key не предоставлен
        """
        if not api_key:
            raise ValueError("API ключ Perplexity обязателен")

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.api_url = self.API_URL
        self.logger = logging.getLogger(__name__)

        self.logger.info(
            f"Инициализирован PerplexityService с моделью {self.model}"
        )

    def _create_search_prompt(self, item_name: str, item_unit: str) -> str:
        """
        Создает промпт для поиска рыночных цен.

        Args:
            item_name: Название товара или услуги
            item_unit: Единица измерения

        Returns:
            Сформированный промпт для Perplexity API
        """
        prompt = f"""Найди актуальную информацию о рыночных ценах на "{item_name}" в Украине.

Единица измерения: {item_unit}

Предоставь следующую информацию:
1. Средняя рыночная цена за {item_unit}
2. Минимальная цена за {item_unit}
3. Краткий анализ (2-3 предложения) с указанием конкретных источников информации (названия сайтов или магазинов)

Формат ответа должен быть структурированным:
СРЕДНЯЯ ЦЕНА: [число] грн
МИНИМАЛЬНАЯ ЦЕНА: [число] грн
АНАЛИЗ: [текст с указанием источников]

Если информация не найдена, укажи это явно."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Optional[Any]]:
        """
        Парсит ответ от Perplexity API.

        Извлекает среднюю цену, минимальную цену и анализ из текстового ответа.

        Args:
            response_text: Текст ответа от API

        Returns:
            Словарь с ключами:
                - average_price: Средняя цена (float или None)
                - min_price: Минимальная цена (float или None)
                - analysis: Текст анализа (str)
        """
        result: Dict[str, Optional[Any]] = {
            "average_price": None,
            "min_price": None,
            "analysis": "",
        }

        try:
            lines = response_text.strip().split("\n")

            for line in lines:
                line = line.strip()

                # Поиск средней цены
                if "СРЕДНЯЯ ЦЕНА:" in line.upper() or "AVERAGE PRICE:" in line.upper():
                    try:
                        # Извлекаем число из строки
                        price_str = line.split(":")[-1].strip()
                        # Убираем все нечисловые символы кроме точки и запятой
                        price_str = "".join(
                            c for c in price_str if c.isdigit() or c in ".,")
                        price_str = price_str.replace(",", ".")
                        if price_str:
                            result["average_price"] = float(price_str)
                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            f"Не удалось извлечь среднюю цену: {e}"
                        )

                # Поиск минимальной цены
                elif "МИНИМАЛЬНАЯ ЦЕНА:" in line.upper() or "MIN PRICE:" in line.upper():
                    try:
                        price_str = line.split(":")[-1].strip()
                        price_str = "".join(
                            c for c in price_str if c.isdigit() or c in ".,")
                        price_str = price_str.replace(",", ".")
                        if price_str:
                            result["min_price"] = float(price_str)
                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            f"Не удалось извлечь минимальную цену: {e}"
                        )

                # Поиск анализа
                elif "АНАЛИЗ:" in line.upper() or "ANALYSIS:" in line.upper():
                    analysis_text = line.split(":", 1)[-1].strip()
                    # Собираем все последующие строки как часть анализа
                    idx = lines.index(line)
                    remaining_lines = lines[idx + 1:]
                    if remaining_lines:
                        analysis_text += " " + " ".join(
                            l.strip() for l in remaining_lines if l.strip()
                        )
                    result["analysis"] = analysis_text

            # Если анализ не найден по ключевому слову, используем весь текст
            if not result["analysis"]:
                result["analysis"] = response_text.strip()

        except Exception as e:
            self.logger.error(f"Ошибка парсинга ответа: {e}")
            result["analysis"] = response_text.strip()

        return result

    async def search_market_price(
        self, item_name: str, item_unit: str
    ) -> Dict[str, Optional[Any]]:
        """
        Выполняет поиск рыночных цен для товара или услуги.

        Отправляет запрос к Perplexity API для получения информации о ценах
        и возвращает структурированные данные.

        Args:
            item_name: Название товара или услуги
            item_unit: Единица измерения

        Returns:
            Словарь с результатами поиска:
                - average_price: Средняя рыночная цена (float или None)
                - min_price: Минимальная рыночная цена (float или None)
                - analysis: Текстовый анализ с источниками (str)

        Raises:
            aiohttp.ClientError: При ошибках HTTP запроса
            Exception: При других непредвиденных ошибках
        """
        self.logger.info(
            f"Поиск рыночных цен для: {item_name} ({item_unit})"
        )

        prompt = self._create_search_prompt(item_name, item_unit)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Извлекаем текст ответа
                    if "choices" in data and len(data["choices"]) > 0:
                        response_text = data["choices"][0]["message"]["content"]
                        self.logger.debug(f"Получен ответ от Perplexity: {response_text[:200]}...")

                        # Парсим ответ
                        result = self._parse_response(response_text)

                        self.logger.info(
                            f"Результаты поиска: средняя цена={result['average_price']}, "
                            f"мин. цена={result['min_price']}"
                        )

                        return result
                    else:
                        self.logger.warning("Пустой ответ от Perplexity API")
                        return {
                            "average_price": None,
                            "min_price": None,
                            "analysis": "Информация не найдена",
                        }

        except aiohttp.ClientError as e:
            self.logger.error(
                f"Ошибка HTTP запроса к Perplexity API: {e}"
            )
            raise

        except Exception as e:
            self.logger.error(
                f"Непредвиденная ошибка при поиске цен: {e}"
            )
            raise


if __name__ == "__main__":
    import asyncio

    # Пример использования для тестирования
    async def test_service():
        """Тестовая функция для проверки работы сервиса."""
        # Замените на ваш реальный API ключ
        api_key = "your_api_key_here"

        try:
            service = PerplexityService(api_key=api_key)

            # Тест поиска цены на товар
            result = await service.search_market_price(
                item_name="Цемент М500",
                item_unit="мешок 50кг"
            )

            print("Результаты поиска для товара:")
            print(f"Средняя цена: {result['average_price']} грн")
            print(f"Минимальная цена: {result['min_price']} грн")
            print(f"Анализ: {result['analysis']}")
            print()

            # Тест поиска цены на услугу
            result = await service.search_market_price(
                item_name="Штукатурка стен",
                item_unit="м2"
            )

            print("Результаты поиска для услуги:")
            print(f"Средняя цена: {result['average_price']} грн")
            print(f"Минимальная цена: {result['min_price']} грн")
            print(f"Анализ: {result['analysis']}")

        except Exception as e:
            print(f"Ошибка: {e}")

    # Запуск теста
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_service())
