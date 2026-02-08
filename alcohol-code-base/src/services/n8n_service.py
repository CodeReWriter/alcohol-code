import aiohttp
import logging
from typing import Optional
from pathlib import Path

from models.document_analysis import DocumentAnalysis


class N8nService:
    """Сервис для работы с n8n."""

    def __init__(self, n8n_webhook_url: str, timeout: int = 300):
        """
        Инициализация сервиса n8n.

        Args:
            n8n_webhook_url: URL webhook'а n8n для обработки документов
            timeout: Таймаут запроса в секундах
        """
        self.webhook_url = n8n_webhook_url
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    async def analyze_document(
        self, file_path: Path, file_name: str
    ) -> Optional[DocumentAnalysis]:
        """
        Отправляет документ в n8n для анализа.

        Args:
            file_path: Путь к файлу документа
            file_name: Имя файла

        Returns:
            Результат анализа документа или None в случае ошибки
        """
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                with open(file_path, "rb") as file:
                    data = aiohttp.FormData()
                    data.add_field("file", file, filename=file_name)

                    async with session.post(self.webhook_url, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            return GoodsDocumentAnalysis.model_validate(result)
                        else:
                            self.logger.error(
                                f"n8n вернул статус {response.status}: {await response.text()}"
                            )
                            return None

        except aiohttp.ClientError as e:
            self.logger.error(f"Ошибка при отправке запроса в n8n: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при анализе документа: {e}")
            return None
