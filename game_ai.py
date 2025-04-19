# game_ai.py
"""
Модуль AI для игры крестики-нолики: алгоритм Minimax для выбора оптимального хода
"""
from game_logic import check_winner


def minimax(board: list, is_maximizing: bool, ai_symbol: str, human_symbol: str) -> dict:
    """Рекурсивная функция Minimax"""
    winner, combo = check_winner(board)
    if winner:
        if winner == human_symbol:
            return {"score": -1}
        elif winner == ai_symbol:
            return {"score": 1}
        else:
            return {"score": 0}
    if is_maximizing:
        best = {"score": -2, "index": None}
        for i, cell in enumerate(board):
            if isinstance(cell, int):
                board_copy = board.copy()
                board_copy[i] = ai_symbol
                sim = minimax(board_copy, False, ai_symbol, human_symbol)
                if sim["score"] > best["score"]:
                    best = {"score": sim["score"], "index": i}
        return best
    else:
        best = {"score": 2, "index": None}
        for i, cell in enumerate(board):
            if isinstance(cell, int):
                board_copy = board.copy()
                board_copy[i] = human_symbol
                sim = minimax(board_copy, True, ai_symbol, human_symbol)
                if sim["score"] < best["score"]:
                    best = {"score": sim["score"], "index": i}
        return best


def best_move(board: list, ai_symbol: str, human_symbol: str) -> int:
    """Возвращает индекс лучшего хода для AI"""
    result = minimax(board, True, ai_symbol, human_symbol)
    return result.get("index") 