import json
import logging
from typing import Optional
from pathlib import Path
from google import genai
from PIL import Image

from config import get_settings
from enums.sheets import Sheet
from models.document_analysis import DocumentAnalysis
from models.document_goods import GoodsDocumentAnalysis
from models.document_jobs import JobsDocumentAnalysis
from prompts import GOODS_INVOICE_ANALYSIS_PROMPT, JOBS_INVOICE_ANALYSIS_PROMPT

settings = get_settings()
GEMINI_MODEL_NAME = settings.gemini.model


class GeminiService:
    """Сервис для работы с Google Gemini."""

    def __init__(self, api_key: str, model_name: str = GEMINI_MODEL_NAME):
        """
        Инициализация сервиса Gemini.

        Args:
            api_key: API ключ для Gemini
            model_name: Название модели Gemini
        """
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Gemini: {e}")
            raise

    async def analyze_invoice_image(
        self,
        image_path: Path,
        document_type: Sheet,
    ) -> Optional[DocumentAnalysis]:
        """
        Анализирует изображение накладной с помощью Gemini.

        Args:
            image_path: Путь к изображению

        Returns:
            Результат анализа документа или None в случае ошибки
        """
        try:
            # Открываем и подготавливаем изображение
            image = Image.open(image_path)

            # Оптимизируем размер изображения для экономии токенов
            # max_size = 1024
            # if max(image.size) > max_size:
            #     ratio = max_size / max(image.size)
            #     new_size = tuple(int(dim * ratio) for dim in image.size)
            #     image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Конвертируем в RGB если необходимо
            if image.mode != "RGB":
                image = image.convert("RGB")

            self.logger.info(
                f"Отправляем изображение {image_path.name} в Gemini для анализа"
            )

            # Сохраняем оптимизированное изображение во временный файл
            temp_image_path = image_path.parent / f"temp_{image_path.name}"
            image.save(temp_image_path, format="JPEG", quality=95)

            try:
                # Загружаем изображение в Gemini
                uploaded_file = self.client.files.upload(file=str(temp_image_path))

                self.logger.info(
                    f"{'=' * 30}\n"
                    f"document_type = {document_type} \n"
                    f"choice = {'GOODS_INVOICE_ANALYSIS_PROMPT' if document_type == Sheet.MATERIALS else 'JOBS_INVOICE_ANALYSIS_PROMPT'}"
                )

                # Отправляем запрос в Gemini
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        genai.types.Content(
                            parts=[
                                genai.types.Part.from_text(
                                    text=(
                                        GOODS_INVOICE_ANALYSIS_PROMPT
                                        if document_type == Sheet.MATERIALS
                                        else JOBS_INVOICE_ANALYSIS_PROMPT
                                    ),
                                ),
                                genai.types.Part.from_uri(
                                    file_uri=uploaded_file.uri,
                                    mime_type=uploaded_file.mime_type,
                                ),
                            ]
                        )
                    ],
                )

                # Удаляем временный файл
                temp_image_path.unlink(missing_ok=True)

                if not response.text:
                    self.logger.error("Gemini вернул пустой ответ")
                    return None

                # Парсим JSON ответ
                try:
                    # Очищаем ответ от возможных markdown блоков
                    response_text = response.text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()

                    result_data = json.loads(response_text)

                    # Выводим результаты для дебага
                    print(result_data)  # Debugging purposes

                    # Валидируем и создаем объект DocumentAnalysis
                    if document_type == Sheet.MATERIALS:
                        analysis = GoodsDocumentAnalysis.model_validate(result_data)
                    elif document_type == Sheet.JOBS:
                        analysis = JobsDocumentAnalysis.model_validate(result_data)
                    else:
                        self.logger.error(f"Неизвестный document_type: {document_type}")
                        return None

                    self.logger.info(
                        f"Успешно проанализировано изображение {image_path.name}"
                    )
                    return analysis

                except json.JSONDecodeError as e:
                    self.logger.error(f"Ошибка парсинга JSON ответа от Gemini: {e}")
                    self.logger.error(f"Ответ Gemini: {response.text}")
                    return None
                except Exception as e:
                    self.logger.error(f"Ошибка валидации данных от Gemini: {e}")
                    return None

            finally:
                # Убеждаемся, что временный файл удален
                temp_image_path.unlink(missing_ok=True)

        except Exception as e:
            self.logger.error(f"Ошибка при анализе изображения через Gemini: {e}")
            return None

    async def analyze_document(
        self,
        document_path: Path,
        document_type: Sheet,
    ) -> Optional[DocumentAnalysis]:
        """
        Анализирует документ (PDF, DOCX) с помощью Gemini.

        Args:
            document_path: Путь к документу
            document_type: Тип документа (товары или услуги)

        Returns:
            Результат анализа документа или None в случае ошибки
        """
        try:
            self.logger.info(
                f"Отправляем документ {document_path.name} в Gemini для анализа"
            )

            # Загружаем документ в Gemini
            uploaded_file = self.client.files.upload(file=str(document_path))

            self.logger.info(
                f"{'=' * 30}\n"
                f"document_type = {document_type} \n"
                f"choice = {'GOODS_INVOICE_ANALYSIS_PROMPT' if document_type == Sheet.MATERIALS else 'JOBS_INVOICE_ANALYSIS_PROMPT'}"
            )

            # Отправляем запрос в Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    genai.types.Content(
                        parts=[
                            genai.types.Part.from_text(
                                text=(
                                    GOODS_INVOICE_ANALYSIS_PROMPT
                                    if document_type == Sheet.MATERIALS
                                    else JOBS_INVOICE_ANALYSIS_PROMPT
                                ),
                            ),
                            genai.types.Part.from_uri(
                                file_uri=uploaded_file.uri,
                                mime_type=uploaded_file.mime_type,
                            ),
                        ]
                    )
                ],
            )

            if not response.text:
                self.logger.error("Gemini вернул пустой ответ")
                return None

            # Парсим JSON ответ
            try:
                # Очищаем ответ от возможных markdown блоков
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                result_data = json.loads(response_text)

                # Выводим результаты для дебага
                print(result_data)  # Debugging purposes

                # Валидируем и создаем объект DocumentAnalysis
                if document_type == Sheet.MATERIALS:
                    analysis = GoodsDocumentAnalysis.model_validate(result_data)
                elif document_type == Sheet.JOBS:
                    analysis = JobsDocumentAnalysis.model_validate(result_data)
                else:
                    self.logger.error(f"Неизвестный document_type: {document_type}")
                    return None

                self.logger.info(
                    f"Успешно проанализирован документ {document_path.name}"
                )
                return analysis

            except json.JSONDecodeError as e:
                self.logger.error(f"Ошибка парсинга JSON ответа от Gemini: {e}")
                self.logger.error(f"Ответ Gemini: {response.text}")
                return None
            except Exception as e:
                self.logger.error(f"Ошибка валидации данных от Gemini: {e}")
                return None

        except Exception as e:
            self.logger.error(f"Ошибка при анализе документа через Gemini: {e}")
            return None

    def is_document_file(self, file_path: Path) -> bool:
        """
        Определяет, является ли файл документом (PDF, DOCX).

        Args:
            file_path: Путь к файлу

        Returns:
            True, если файл является документом
        """
        try:
            file_extension = file_path.suffix.lower()
            document_extensions = {".pdf", ".docx", ".doc"}
            return file_extension in document_extensions

        except Exception as e:
            self.logger.warning(f"Ошибка при определении типа документа: {e}")
            return False

    def is_image_file(self, file_path: Path) -> bool:
        """
        Проверяет, является ли файл изображением.

        Args:
            file_path: Путь к файлу

        Returns:
            True если файл является изображением
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
