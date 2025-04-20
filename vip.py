# vip.py
from datetime import datetime

vip_users: set[int] = set()
vip_usernames: set[str] = set()
avatars: dict[int, str] = {}
DEFAULT_AVATAR: str = "🤖"
VIP_ICON: str = "💎"
signatures: dict[int, str] = {}

vip_user_map: dict[int, str] = {}
subscriptions: dict[int, datetime] = {}


def is_vip(user_id: int) -> bool:
    return user_id in vip_users


def is_vip_by_username(username: str) -> bool:
    return username in vip_usernames


def add_vip(user_id: int, username: str = None) -> None:
    # Добавляем VIP и сохраняем время подписки
    vip_users.add(user_id)
    subscriptions[user_id] = datetime.now()
    if username:
        vip_user_map[user_id] = username
        vip_usernames.add(username)


def set_avatar(user_id: int, emoji: str) -> None:
    avatars[user_id] = emoji


def get_avatar(user_id: int) -> str:
    return avatars.get(user_id, DEFAULT_AVATAR)


def set_signature(user_id: int, text: str) -> None:
    """Устанавливает персональную подпись для пользователя"""
    signatures[user_id] = text


def get_signature(user_id: int) -> str:
    """Возвращает персональную подпись пользователя или пустую строку"""
    return signatures.get(user_id, "")


def get_subscription_time(user_id: int) -> datetime | None:
    """Возвращает время начала подписки или None"""
    return subscriptions.get(user_id) 