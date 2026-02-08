from aiogram.fsm.state import StatesGroup, State


class DocumentProcessing(StatesGroup):
    """
    Состояния для процесса обработки документов.

    Атрибуты:
        waiting_for_project_selection: Ожидание выбора проекта
        waiting_for_document_type_selection: Ожидание выбора типа документа (услуги/товары)
        waiting_for_document: Ожидание загрузки документа
        processing: Процесс обработки документа
    """

    waiting_for_project_selection = State()
    waiting_for_document_type_selection = State()
    waiting_for_document = State()
    processing = State()
