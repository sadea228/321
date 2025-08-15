import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from game_ai import best_move, minimax


def test_best_move_finds_winning_move():
    board = ["X", "X", 2, "O", "O", 5, 6, 7, 8]
    assert best_move(board, "X", "O") == 2


def test_minimax_returns_negative_score_for_human_win():
    board = ["O", "O", "O", 3, 4, 5, 6, 7, 8]
    result = minimax(board, True, "X", "O")
    assert result["score"] == -1


def test_minimax_returns_positive_score_for_ai_win():
    board = ["X", "X", "X", 3, 4, 5, 6, 7, 8]
    result = minimax(board, False, "X", "O")
    assert result["score"] == 1


def test_minimax_returns_zero_for_draw():
    board = ["X", "O", "X", "X", "O", "X", "O", "X", "O"]
    result = minimax(board, True, "X", "O")
    assert result["score"] == 0
