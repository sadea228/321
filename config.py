import logging
import os

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# --- Константы и темы ---
DEFAULT_THEME_KEY = "classic"
EMPTY_CELL_SYMBOL = "empty"  # Внутренний ключ для пустой клетки в теме

THEMES = {
    "classic": {
        "name": "Классика",
        "X": "❌",
        "O": "⭕",
        EMPTY_CELL_SYMBOL: "⬜",
        "X_win": "⭐❌⭐",
        "O_win": "⭐⭕⭐",
    },
    "animals": {
        "name": "Животные",
        "X": "🐱",
        "O": "🐶",
        EMPTY_CELL_SYMBOL: "🐾",
        "X_win": "🏆🐱🏆",
        "O_win": "🏆🐶🏆",
    },
    "food": {
        "name": "Еда",
        "X": "🍕",
        "O": "🍔",
        EMPTY_CELL_SYMBOL: "▫️",
        "X_win": "🌟🍕🌟",
        "O_win": "🌟🍔🌟",
    },
    "space": {
        "name": "Космос",
        "X": "🚀",
        "O": "🛸",
        EMPTY_CELL_SYMBOL: "🌑",
        "X_win": "🌟🚀🌟",
        "O_win": "🌟🛸🌟",
    },
    "sports": {
        "name": "Спорт",
        "X": "🎾",
        "O": "⚽",
        EMPTY_CELL_SYMBOL: "🏟️",
        "X_win": "🏆🎾🏆",
        "O_win": "🏆⚽🏆",
    },
    # Добавьте сюда другие темы при желании
}

# --- Настройки ---
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("Необходимо установить переменную окружения TOKEN!")

# Таймаут ожидания второго игрока
GAME_TIMEOUT_SECONDS = 90
