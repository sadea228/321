"""
Обработчики для игры против ИИ с использованием алгоритма Minimax из game_ai.py
"""
import asyncio
import telegram
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.helpers import escape_markdown

from config import THEMES, DEFAULT_THEME_KEY
from game_state import games, chat_stats
from game_logic import get_symbol_emoji, get_keyboard, check_winner
from game_ai import best_move
from handlers.game_handlers import _restore_game_message

async def play_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начать игру пользователя против ИИ"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    username = user.username or f"player_{user_id}"
    message = update.effective_message or update.message

    # Проверка активной игры
    if chat_id in games and not games[chat_id].get('game_over', True):
        await message.reply_text("⏳ В этом чате уже идет игра. Сначала завершите ее.")
        return

    # Сброс предыдущей игры
    if chat_id in games:
        del games[chat_id]

    # Инициализация
    chosen_key = context.user_data.get('chosen_theme', DEFAULT_THEME_KEY)
    theme_emojis = THEMES.get(chosen_key, THEMES[DEFAULT_THEME_KEY])
    # Пользователь всегда X, ИИ всегда O
    user_symbol = 'X'
    ai_symbol = 'O'
    board = list(range(1, 10))
    game_data = {
        'board': board,
        'current_player': user_symbol,
        'game_over': False,
        'players': {user_symbol: user_id, ai_symbol: "AI"},
        'user_symbols': {user_id: user_symbol},
        'usernames': {user_id: username, 'AI': '🤖 ИИ'},
        'theme_emojis': theme_emojis,
        'vs_ai': True,
        'ai_symbol': ai_symbol,
        'last_move': None
    }
    games[chat_id] = game_data

    # Отправка стартового сообщения
    user_emoji = get_symbol_emoji(user_symbol, theme_emojis)
    text = (
        f"<b>🤖 Игра против ИИ</b>\n"
        "────────────────\n"
        f"👤 {user_emoji}: <i>{escape_markdown(username, version=1)}</i>\n"
        "────────────────\n"
        "<i>Ваш ход! Нажмите на клетку.</i>"
    )
    sent = await message.reply_text(
        text,
        reply_markup=get_keyboard(chat_id),
        parse_mode="HTML"
    )
    game_data['message_id'] = sent.message_id

async def ai_move(query: telegram.CallbackQuery, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    """Выполняет ход ИИ и обновляет сообщение"""
    game_data = games[chat_id]
    board = game_data['board']
    ai_symbol = game_data['ai_symbol']
    human_symbol = 'X' if ai_symbol == 'O' else 'O'

    # Вычисляем лучший ход
    move = best_move(board, ai_symbol, human_symbol)
    if move is None:
        return
    # Анимация хода ИИ
    await asyncio.sleep(0.5)
    board[move] = ai_symbol
    # Сохраняем индекс последнего хода для подсветки
    game_data['last_move'] = move
    winner, combo = check_winner(board)
    # Завершаем или продолжаем игру
    if winner:
        game_data['game_over'] = True
        # Обновляем статистику чата
        stats = chat_stats.setdefault(chat_id, {"games": 0, "wins": 0, "draws": 0, "top_players": {}})
        stats["games"] += 1
        if winner == "Ничья":
            stats["draws"] += 1
            text = "🤝 Ничья!"
            keyboard = get_keyboard(chat_id)
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
        else:
            stats["wins"] += 1
            # Имя победителя
            winner_id = game_data['players'][winner]
            winner_name = game_data['usernames'].get(winner_id, str(winner_id))
            stats["top_players"][winner_name] = stats["top_players"].get(winner_name, 0) + 1
            theme_emojis = game_data['theme_emojis']
            winner_emoji = get_symbol_emoji(f"{winner}_win", theme_emojis)
            text = f"🏆 Победитель: {escape_markdown(winner_name, version=1)} {winner_emoji}! Поздравляем!"
            keyboard = get_keyboard(chat_id, combo)
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # Переключаем ход на пользователя и обновляем сообщение
        game_data['current_player'] = human_symbol
        await _restore_game_message(query, context, chat_id, theme_changed=False)

# Создаем handler для команды /play_ai
play_ai_handler = CommandHandler("play_ai", play_ai) 