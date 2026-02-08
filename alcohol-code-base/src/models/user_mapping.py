from typing import Dict

from pydantic import BaseModel, Field


class UserMapping(BaseModel):
    """
    Модель для хранения сопоставлений пользователей.

    Args:
        id_to_username: Словарь для поиска username по ID.
        username_to_id: Словарь для поиска ID по username.
    """

    id_to_username: Dict[str, str] = Field(default_factory=dict)
    username_to_id: Dict[str, str] = Field(default_factory=dict)
