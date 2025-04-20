# vip.py
from datetime import datetime
import json
import os

vip_users: set[int] = set()
vip_usernames: set[str] = set()
avatars: dict[int, str] = {}
DEFAULT_AVATAR: str = "🤖"
VIP_ICON: str = "💎"
signatures: dict[int, str] = {}

vip_user_map: dict[int, str] = {}
subscriptions: dict[int, datetime] = {}

# Добавление: хранение и функции пользовательских символов для VIP
custom_symbols: dict[int, str] = {}

VIP_DATA_FILE = os.path.join(os.path.dirname(__file__), 'vip_data.json')

# Функции для сохранения и загрузки VIP-данных
def load_vip_data() -> None:
    if os.path.exists(VIP_DATA_FILE):
        with open(VIP_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            vip_users.update(data.get('vip_users', []))
            vip_usernames.update(data.get('vip_usernames', []))
            avatars.update(data.get('avatars', {}))
            signatures.update(data.get('signatures', {}))
            custom_symbols.update(data.get('custom_symbols', {}))
            subscriptions.update({int(k): datetime.fromisoformat(v) for k, v in data.get('subscriptions', {}).items()})

def save_vip_data() -> None:
    data = {
        'vip_users': list(vip_users),
        'vip_usernames': list(vip_usernames),
        'avatars': avatars,
        'signatures': signatures,
        'custom_symbols': custom_symbols,
        'subscriptions': {str(k): v.isoformat() for k, v in subscriptions.items()}
    }
    with open(VIP_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загружаем данные при старте модуля
load_vip_data()

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
    # Сохраняем изменения
    save_vip_data()


def set_avatar(user_id: int, emoji: str) -> None:
    avatars[user_id] = emoji
    save_vip_data()


def get_avatar(user_id: int) -> str:
    return avatars.get(user_id, DEFAULT_AVATAR)


def set_signature(user_id: int, text: str) -> None:
    """Устанавливает персональную подпись для пользователя"""
    signatures[user_id] = text
    save_vip_data()


def get_signature(user_id: int) -> str:
    """Возвращает персональную подпись пользователя или пустую строку"""
    return signatures.get(user_id, "")


def get_subscription_time(user_id: int) -> datetime | None:
    """Возвращает время начала подписки или None"""
    return subscriptions.get(user_id)


def set_symbol(user_id: int, emoji: str) -> None:
    """Устанавливает пользовательский символ для VIP-пользователя"""
    custom_symbols[user_id] = emoji
    save_vip_data()


def get_symbol(user_id: int) -> str | None:
    """Возвращает пользовательский символ VIP-пользователя или None"""
    return custom_symbols.get(user_id) 