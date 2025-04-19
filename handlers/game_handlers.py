# handlers/game_handlers.py
"""
Handlers for game commands and callbacks.
"""
import random
import asyncio
from datetime import timedelta
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.helpers import escape_markdown
from typing import Optional, List, Tuple

from config import logger, GAME_TIMEOUT_SECONDS, THEMES, DEFAULT_THEME_KEY
from game_state import games, banned_users, chat_stats
from game_logic import get_symbol_emoji, get_keyboard, check_winner
from handlers.ai_handlers import ai_move

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🎉 <b>Добро пожаловать в CrackNolikBot!</b> 🎉\n\n"
        "🔹 /newgame — начать новую игру\n"
        "🔹 /themes — выбрать тему\n",
        parse_mode="HTML"
    )

async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /newgame - создаёт новую игру"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or f"player_{user_id}"
    message = update.effective_message or update.message
    
    # Блокировка забаненных пользователей
    if str(user_id) in banned_users or update.effective_user.username in banned_users:
        await message.reply_text("⛔ Вы забанены и не можете начинать игры.")
        return

    # Проверка на активную игру
    if chat_id in games and not games[chat_id].get('game_over', True):
        await message.reply_text(
            "⏳ В этом чате уже идет игра! Дождитесь ее завершения или отмены.",
            reply_to_message_id=games[chat_id].get('message_id')
        )
        logger.warning(f"Пытались начать игру в чате {chat_id}, где уже есть активная игра.")
        return

    # Отмена старого таймера и удаление старой игры
    if chat_id in games:
        old_job = games[chat_id].get('timeout_job')
        if old_job:
            try:
                old_job.schedule_removal()
                logger.info(f"Removed previous timeout job for chat {chat_id}.")
            except Exception as e:
                logger.warning(f"Could not remove timeout job for chat {chat_id}: {e}")
        del games[chat_id]

    # Инициализация новой игры
    first_player = random.choice(["X", "O"])
    second_player = "O" if first_player == "X" else "X"
    chosen_key = context.user_data.get('chosen_theme', DEFAULT_THEME_KEY)
    theme_emojis = THEMES.get(chosen_key, THEMES[DEFAULT_THEME_KEY])
    game_data = {
        "board": list(range(1, 10)),
        "current_player": first_player,
        "game_over": False,
        "players": {first_player: user_id, second_player: None},
        "user_symbols": {user_id: first_player},
        "usernames": {user_id: username},
        "message_id": None,
        "timeout_job": None,
        "theme_emojis": theme_emojis
    }
    games[chat_id] = game_data

    # Отправка начального сообщения
    first_emoji = get_symbol_emoji(first_player, game_data['theme_emojis'])
    sent_message = await message.reply_text(
        "<b>🕹️ НОВАЯ ИГРА НАЧАЛАСЬ! 🕹️</b>\n"
        "───────────────\n"
        f"👤 Игрок: <i>{escape_markdown(username, version=1)}</i>\n"
        f"🎭 Символ: {first_emoji}\n"
        f"⏱️ Таймаут на ход: {GAME_TIMEOUT_SECONDS} сек\n"
        "───────────────\n"
        "<i>Ждём второго игрока...</i>",
        reply_markup=get_keyboard(chat_id),
        parse_mode="HTML"
    )
    game_data['message_id'] = sent_message.message_id

    # Планируем таймаут ожидания второго игрока
    job_context = {'chat_id': chat_id, 'message_id': sent_message.message_id}
    timeout_job = context.job_queue.run_once(
        game_timeout,
        when=timedelta(seconds=GAME_TIMEOUT_SECONDS),
        data=job_context,
        name=f"game_timeout_{chat_id}"
    )
    game_data['timeout_job'] = timeout_job

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на кнопки игрового поля или управления игрой."""
    query = update.callback_query
    user = update.effective_user
    chat_id = update.effective_chat.id
    data = query.data

    # Блокировка забаненных пользователей
    if str(user.id) in banned_users or user.username in banned_users:
        await query.answer("⛔ Вы забанены и не можете играть.", show_alert=True)
        return

    # Ответ на callback
    try:
        await query.answer()
    except telegram.error.BadRequest:
        pass

    # Проверка наличия игры
    if chat_id not in games:
        await query.answer("Игра не найдена.", show_alert=True)
        return

    game_data = games[chat_id]
    message_id = query.message.message_id if query.message else None
    # Проверка на актуальность сообщения
    if message_id and message_id != game_data.get('message_id'):
        await query.answer("Старая игра. Начните новую.", show_alert=True)
        try:
            await context.bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        except Exception:
            pass
        return

    # Обработка noop и new_game и ходов
    if data == 'noop':
        return
    if data == 'new_game':
        # При нажатии "Новая игра" запускаем новую игру от имени пользователя
        await new_game(update, context)
        return
    if data.isdigit():
        cell = int(data)
        # логика присоединения и хода, проверка победы
        board = game_data['board']
        if isinstance(board[cell], int):
            symbol = game_data['current_player']
            user_id = update.effective_user.id
            # Логика регистрации второго игрока
            if game_data['players'][symbol] is None:
                other_symbol = 'O' if symbol == 'X' else 'X'
                # Запрещаем одному пользователю играть за обе стороны
                if game_data['players'][other_symbol] == user_id:
                    await query.answer("Вы уже играете за другую сторону", show_alert=True)
                    return
                # Регистрация второго игрока и отмена таймаута ожидания второго игрока
                game_data['players'][symbol] = user_id
                game_data['user_symbols'][user_id] = symbol
                # Сохраняем имя второго игрока
                username = update.effective_user.username or f"player_{user_id}"
                game_data['usernames'][user_id] = username
                if game_data.get('timeout_job'):
                    try:
                        game_data['timeout_job'].schedule_removal()
                        logger.info(f"Second player joined for chat {chat_id}, canceled timeout")
                    except Exception as e:
                        logger.warning(f"Could not cancel timeout job for chat {chat_id}: {e}")
                    game_data['timeout_job'] = None
            elif game_data['players'][symbol] != user_id:
                await query.answer("Сейчас не ваш ход", show_alert=True)
                return
            # Анимация хода: показываем анимированные эмодзи
            keyboard = get_keyboard(chat_id)
            row, col = divmod(cell, 3)
            frames = ["⏳", "⌛️", "⏳"]
            for frame in frames:
                animated_keyboard = []
                for r_i, row_buttons in enumerate(keyboard.inline_keyboard):
                    new_row = []
                    for c_i, btn in enumerate(row_buttons):
                        if r_i == row and c_i == col:
                            new_row.append(InlineKeyboardButton(frame, callback_data="noop"))
                        else:
                            new_row.append(btn)
                    animated_keyboard.append(new_row)
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(animated_keyboard))
                await asyncio.sleep(0.2)
            # Устанавливаем символ в ячейку после анимации
            board[cell] = symbol
            # Сохраняем индекс последнего хода для подсветки
            game_data['last_move'] = cell
            winner, combo = check_winner(board)
            if winner:
                # Завершаем игру и подсчитываем метрики
                game_data['game_over'] = True
                # Обновляем статистику чата
                stats = chat_stats.setdefault(chat_id, {"games": 0, "wins": 0, "draws": 0, "top_players": {}})
                stats["games"] += 1
                if winner == "Ничья":
                    stats["draws"] += 1
                    # Отображаем сообщение о ничье с финальным полем
                    theme_emojis = game_data['theme_emojis']
                    text = "🤝 Ничья!"
                    keyboard = get_keyboard(chat_id)
                    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
                else:
                    stats["wins"] += 1
                    # Ваш победитель
                    winner_id = game_data['players'][winner]
                    winner_name = game_data['usernames'].get(winner_id, str(winner_id))
                    stats["top_players"][winner_name] = stats["top_players"].get(winner_name, 0) + 1
                    # Подготовка текста с именем и эмодзи победителя
                    theme_emojis = game_data['theme_emojis']
                    winner_emoji = get_symbol_emoji(f"{winner}_win", theme_emojis)
                    text = f"🏆 Победитель: {escape_markdown(winner_name, version=1)} {winner_emoji}! Поздравляем!"
                    keyboard = get_keyboard(chat_id, combo)
                    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                game_data['current_player'] = 'O' if symbol == 'X' else 'X'
                # Если игра против ИИ, выполняем ход ИИ, иначе обновляем сообщение
                if game_data.get('vs_ai'):
                    await ai_move(query, context, chat_id)
                else:
                    await _restore_game_message(query, context, chat_id, theme_changed=False)
        return

async def game_timeout(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик таймаута ожидания второго игрока."""
    job = context.job.data
    chat_id = job['chat_id']
    if chat_id in games:
        game_data = games[chat_id]
        if not game_data.get('game_over') and not game_data['players'].get('O' if game_data['current_player']=='X' else 'X'):
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=job['message_id'],
                text="⌛ Время вышло! Игра отменена.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Новая игра", callback_data="new_game")]])
            )
            game_data['game_over'] = True
            game_data['timeout_job'] = None

async def _restore_game_message(query: telegram.CallbackQuery, context: ContextTypes.DEFAULT_TYPE, chat_id: int, theme_changed: bool) -> None:
    """Восстанавливает сообщение об игре при смене темы или ходе."""
    game_data = games[chat_id]
    # Информация об игроках
    x_id = game_data['players'].get('X')
    o_id = game_data['players'].get('O')
    x_name = game_data['usernames'].get(x_id, '—') if x_id else '—'
    o_name = game_data['usernames'].get(o_id, '—') if o_id else '—'
    emojis = game_data['theme_emojis']
    x_emoji = get_symbol_emoji('X', emojis)
    o_emoji = get_symbol_emoji('O', emojis)
    current = game_data['current_player']
    current_emoji = get_symbol_emoji(current, emojis)
    title = "🎨 Тема изменена! 🎨\n\n" if theme_changed else ""
    text = (
        f"{title}<b>🔄 ИГРА В ПРОЦЕССЕ</b> 🔄\n"
        "────────────────\n"
        f"👤 {x_emoji}: <i>{escape_markdown(x_name, version=1)}</i>\n"
        f"👤 {o_emoji}: <i>{escape_markdown(o_name, version=1)}</i>\n"
        "────────────────\n"
        f"➡️ <b>Ходит: {current_emoji}</b>"
    )
    await query.edit_message_text(
        text,
        reply_markup=get_keyboard(chat_id),
        parse_mode="HTML"
    )

# Handler objects
start_handler = CommandHandler("start", start)
new_game_handler = CommandHandler("newgame", new_game)
button_click_handler = CallbackQueryHandler(button_click, pattern=r"^(noop|[0-8]|new_game)$") 