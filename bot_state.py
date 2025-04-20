"""
Модуль для хранения списка чатов, в которых бот активен (для рассылок).
"""
all_chats: set[int] = set()

def add_chat(chat_id: int) -> None:
    """Добавляет идентификатор чата в список"""
    all_chats.add(chat_id)

def get_all_chats() -> set[int]:
    """Возвращает множество всех известных чатов"""
    return all_chats 