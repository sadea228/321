import logging
import os

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# --- Константы и темы ---
DEFAULT_THEME_KEY = "classic"
EMPTY_CELL_SYMBOL = "empty" # Внутренний ключ для пустой клетки в теме

THEMES = {
    "classic": {
        "name": "Классика",
        "X": "❌",
        "O": "⭕",
        EMPTY_CELL_SYMBOL: "⬜",
        "X_win": "⭐❌⭐",
        "O_win": "⭐⭕⭐"
    },
    "animals": {
        "name": "Животные",
        "X": "🐱",
        "O": "🐶",
        EMPTY_CELL_SYMBOL: "🐾",
        "X_win": "🏆🐱🏆",
        "O_win": "🏆🐶🏆"
    },
    "food": {
        "name": "Еда",
        "X": "🍕",
        "O": "🍔",
        EMPTY_CELL_SYMBOL: "▫️",
        "X_win": "🌟🍕🌟",
        "O_win": "🌟🍔🌟"
    }
    # Добавьте сюда другие темы при желании
}

# --- Настройки для вебхука ---
# Получаем токен из переменной окружения
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("Необходимо установить переменную окружения TOKEN!")
    # В реальном приложении здесь лучше выбросить исключение или использовать значение по умолчанию для тестов
    # exit(1) # Не будем прерывать выполнение здесь, пусть это произойдет в bot.py при инициализации

# URL для вебхука (Render предоставляет RENDER_EXTERNAL_URL)
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")
# Локальный URL для тестирования (если RENDER_EXTERNAL_URL не задан)
if not WEBHOOK_URL:
   logger.warning("RENDER_EXTERNAL_URL не установлена. Используется заглушка для локального теста. Установите WEBHOOK_URL вручную для продакшена.")
   WEBHOOK_URL = "https://your-temporary-render-url" # Замените реальным URL или оставьте заглушку

# Порт для веб-сервера (Render предоставляет PORT)
PORT = int(os.getenv("PORT", "8080"))

# Путь для вебхука (должен совпадать в set_webhook и в endpoint)
WEBHOOK_PATH = "/webhook"
# Полный URL для установки вебхука (формируется здесь для ясности)
WEBHOOK_ENDPOINT_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}" if WEBHOOK_URL else None

# Таймаут ожидания второго игрока
GAME_TIMEOUT_SECONDS = 90 