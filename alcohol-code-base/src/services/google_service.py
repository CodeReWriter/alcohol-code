import json
from datetime import datetime, date

import gspread
import logging
from typing import Optional
from pathlib import Path
from google.auth.exceptions import GoogleAuthError
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError

from models.document_analysis import DocumentAnalysis
from config import settings


class GoogleService:
    """Сервис для работы с Google Sheets."""

    def __init__(self, credentials_path: Path, delegated_user_email: str = None):
        """
        Инициализация сервиса Google.

        Args:
            credentials_path: Путь к файлу с учетными данными Google.
            delegated_user_email: Email пользователя для делегирования прав.
        """
        self.credentials_path = credentials_path
        self.delegated_user_email = delegated_user_email
        self.logger = logging.getLogger(__name__)
        self._sheets_client = None

    async def add_data_to_spreadsheet(
        self,
        analysis: DocumentAnalysis,
        user_id: int,
        first_name: str,
        spreadsheet_id: str,
        sheet_name: str,
    ) -> Optional[str]:
        """
        Добавляет данные анализа в существующую Google таблицу.

        Args:
            analysis: Результат анализа документа
            user_id: ID пользователя Telegram
            first_name: first_name аккаунта пользователя Telegram
            spreadsheet_id: ID Google таблицы
            sheet_name: имя листа в Google таблице

        Returns:
            URL таблицы или None в случае ошибки.
        """
        try:
            client = await self._get_sheets_client()
            if not client:
                self.logger.error("Client Google таблицы не создан")
                return None

            # spreadsheet_id = settings.google.sheets_template_id
            if not spreadsheet_id:
                self.logger.error(
                    f"ID Google таблицы указан неверно: {spreadsheet_id}  не найден"
                )
                return None

            spreadsheet = client.open_by_key(spreadsheet_id)
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                self.logger.warning(f"Лист {sheet_name} не найден в шаблоне")
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows="10000", cols="20"
                )

            # Проверяем, есть ли заголовки, и добавляем их при необходимости
            try:
                existing_headers = worksheet.row_values(1)
            except gspread.exceptions.APIError as e:
                # Если лист пуст, API gspread вернет ошибку
                if "The requested range is empty" in str(e):
                    existing_headers = []
                else:
                    raise

            if not existing_headers:
                headers = [
                    # "Тип документа",
                    "№",
                    "Дата",
                    # "Покупатель",
                    "Найменування",
                    "Од вим",
                    "К-сть",
                    "Цiна",
                    "Сума",
                    "Постачальник",
                    "Примiтки",
                    "Дата внесення",
                    "TelegramID / First Name",
                ]
                worksheet.append_row(headers)

            # Формируем и добавляем строки с данными
            rows_to_add = []
            for item in analysis.items:
                row = [
                    # analysis.document_type or "",
                    analysis.document_number or "",
                    analysis.date,
                    # analysis.customer or "",
                    item.name,
                    item.unit.lower(),
                    item.quantity,
                    item.price,
                    item.total,
                    analysis.supplier or "",
                    "",  # Примечание
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"{str(user_id)} / {first_name}",
                ]
                rows_to_add.append(row)

            if rows_to_add:
                worksheet.append_rows(rows_to_add)

            self.logger.info(
                f"Добавлено {len(rows_to_add)} строк в таблицу для пользователя {user_id}"
            )
            return spreadsheet.url

        except gspread.exceptions.SpreadsheetNotFound:
            self.logger.error(
                f"Таблица с ID '{spreadsheet_id}' не найдена. "
                "Проверьте так же права доступа сервисного аккаунта."
            )
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении данных в Google таблицу: {e}")
            return None

    async def check_sheet_write_permissions(self, sheet_id: str) -> bool:
        """
        Проверяет права на запись в Google таблицу.

        Args:
            sheet_id: ID Google таблицы.

        Returns:
            True, если есть права на запись, иначе False.
        """
        try:
            client = await self._get_sheets_client()

            spreadsheet = client.open_by_key(sheet_id)

            # Проверка наличия страниц 'jobs' и 'materials' в файле
            try:
                ws = spreadsheet.worksheet("materials")
            except gspread.exceptions.WorksheetNotFound:
                self.logger.warning("Лист 'materials' не найден в файле")
                return False
            try:
                _ = spreadsheet.worksheet("jobs")
            except gspread.exceptions.WorksheetNotFound:
                self.logger.warning("Лист 'jobs' не найден в файле")
                return False

            # Проверка возможности записи в 'materials'
            ws.update([["test"]], "A1")
            ws.update([[""]], "A1")

            self.logger.info(
                f"Проверка прав на запись для таблицы {sheet_id} прошла успешно."
            )
            return True
        except HttpError as e:
            if e.resp.status in [403, 404]:
                self.logger.warning(
                    f"Нет прав на запись или таблица не найдена. ID: {sheet_id}. Ошибка: {e}"
                )
            else:
                self.logger.error(
                    f"Ошибка при проверке прав на запись для таблицы {sheet_id}: {e}"
                )
            return False
        except Exception as e:
            self.logger.error(
                f"Непредвиденная ошибка при проверке прав на запись для {sheet_id}: {e}"
            )
            return False

    def get_service_account_email(self) -> str | None:
        """
        Получает email учетной записи для сервисного аккаунта.

        Returns:
             Email учетной записи для сервисного аккаунта или None в случае ошибки.
        """
        try:
            with open(self.credentials_path, "r", encoding="utf-8") as f:
                credentials_data = json.load(f)
                email = credentials_data.get("client_email")
                if not email:
                    self.logger.error("client_email не найден в файле учетных данных")
                    raise ValueError("client_email не найден в файле учетных данных")
        except Exception as ex:
            self.logger.error(f"Ошибка при получении email учетной записи: {ex}")
            return None

        return email

    async def _get_sheets_client(self) -> Optional[gspread.Client]:
        """
        Получает авторизованный клиент для работы с Google Sheets.

        Returns:
            Клиент gspread или None в случае ошибки.
        """
        try:
            if not self._sheets_client:
                self._sheets_client = gspread.service_account(
                    filename=str(self.credentials_path)
                )
            return self._sheets_client
        except GoogleAuthError as e:
            self.logger.error(f"Ошибка аутентификации Google Sheets: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при создании клиента Google Sheets: {e}")
            return None

    async def _get_credentials_with_delegation(self) -> Optional[Credentials]:
        """
        Получает учетные данные с делегированием прав.

        Returns:
            Объект учетных данных или None в случае ошибки.
        """
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            credentials = Credentials.from_service_account_file(
                str(self.credentials_path), scopes=scopes
            )

            if self.delegated_user_email:
                credentials = credentials.with_subject(self.delegated_user_email)
                self.logger.info(
                    f"Используется делегирование прав для: {self.delegated_user_email}"
                )

            return credentials
        except FileNotFoundError:
            self.logger.error(f"Файл учетных данных не найден: {self.credentials_path}")
            return None
        except Exception as ex:
            self.logger.error(f"Ошибка при получении данных делегирования: {ex}")
            return None
