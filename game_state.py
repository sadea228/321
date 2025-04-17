# Словарь для хранения состояния игр {chat_id: game_data}
games: dict[int, dict] = {} 

# Словарь для хранения забаненных пользователей (по username или user_id)
banned_users: set[str] = set()

# Словарь для хранения статистики по чатам
# Формат: {chat_id: {"games": int, "wins": int, "draws": int, "top_players": dict}}
chat_stats: dict[int, dict] = {} 