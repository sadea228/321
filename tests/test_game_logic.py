import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from game_logic import get_symbol_emoji, check_winner, get_keyboard
from game_state import games
from config import THEMES, DEFAULT_THEME_KEY, EMPTY_CELL_SYMBOL


def setup_function(function):
    games.clear()


def test_get_symbol_emoji_returns_x_emoji():
    theme = THEMES[DEFAULT_THEME_KEY]
    assert get_symbol_emoji("X", theme) == theme["X"]


def test_get_symbol_emoji_empty_cell_returns_theme_symbol():
    theme = THEMES[DEFAULT_THEME_KEY]
    assert get_symbol_emoji(0, theme) == theme[EMPTY_CELL_SYMBOL]


def test_get_symbol_emoji_win_fallback():
    theme = {"X": "A", "O": "B", EMPTY_CELL_SYMBOL: "C"}
    assert get_symbol_emoji("X_win", theme) == "⭐❌⭐"


def test_check_winner_row():
    board = ["X", "X", "X", 3, 4, 5, 6, 7, 8]
    winner, combo = check_winner(board)
    assert winner == "X"
    assert combo == [0, 1, 2]


def test_check_winner_draw():
    board = ["X", "O", "X", "X", "O", "X", "O", "X", "O"]
    winner, combo = check_winner(board)
    assert winner == "Ничья"
    assert combo is None


def test_check_winner_none():
    board = ["X", "O", "X", 3, "O", 5, 6, 7, 8]
    winner, combo = check_winner(board)
    assert winner is None
    assert combo is None


def test_get_keyboard_nonexistent_game_returns_none():
    assert get_keyboard(12345) is None


def test_get_keyboard_highlights_last_move():
    games[1] = {
        "board": ["X", 1, 2, 3, 4, 5, 6, 7, 8],
        "game_over": False,
        "theme_emojis": THEMES[DEFAULT_THEME_KEY],
        "last_move": 0,
    }
    markup = get_keyboard(1)
    text = markup.inline_keyboard[0][0].text
    assert "🟩" in text
    assert THEMES[DEFAULT_THEME_KEY]["X"] in text


def test_get_symbol_emoji_returns_o_emoji():
    theme = THEMES[DEFAULT_THEME_KEY]
    assert get_symbol_emoji("O", theme) == theme["O"]


def test_check_winner_diagonal_o():
    board = [0, 1, "O", 3, "O", 5, "O", 7, 8]
    winner, combo = check_winner(board)
    assert winner == "O"
    assert combo == [2, 4, 6]


def test_get_keyboard_highlights_winning_cells_and_shows_new_game_button():
    games[1] = {
        "board": ["X", "X", "X", 3, 4, 5, 6, 7, 8],
        "game_over": True,
        "theme_emojis": THEMES[DEFAULT_THEME_KEY],
    }
    markup = get_keyboard(1, [0, 1, 2])
    assert markup.inline_keyboard[0][0].text == THEMES[DEFAULT_THEME_KEY]["X_win"]
    assert markup.inline_keyboard[-1][0].text == "🔄 Новая игра"
