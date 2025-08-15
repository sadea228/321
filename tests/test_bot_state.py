import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from bot_state import add_chat, get_all_chats, all_chats


def setup_function(function):
    all_chats.clear()


def test_add_chat_adds_chat_id():
    add_chat(123)
    assert 123 in all_chats


def test_get_all_chats_returns_all_ids():
    add_chat(1)
    add_chat(2)
    assert get_all_chats() == {1, 2}
