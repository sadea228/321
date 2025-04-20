# handlers/theme_handlers.py
"""
Handlers for theme selection commands and callbacks.
"""
import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.helpers import escape_markdown

from config import THEMES, DEFAULT_THEME_KEY
from game_state import games
from vip import get_symbol

async def themes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /themes - показывает доступные темы."""
    user_id = update.effective_user.id
    chosen_key = context.user_data.get('chosen_theme', DEFAULT_THEME_KEY)
    current_theme = THEMES.get(chosen_key, THEMES[DEFAULT_THEME_KEY])

    buttons = []
    for key, theme in THEMES.items():
        text = f"{theme['name']} {theme['X']}/{theme['O']}"
        if key == chosen_key:
            text = f"✅ {text}"
        buttons.append([InlineKeyboardButton(text, callback_data=f"theme_select_{key}")])

    await update.message.reply_text(
        f"🎨 *Выбор темы игры* 🎨\n\n"
        f"Текущая тема: *{current_theme['name']} {current_theme['X']}/{current_theme['O']}*\n\n"
        f"Выберите новую тему:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def select_theme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора темы из меню /themes."""
    query = update.callback_query
    await query.answer()

    theme_key = query.data.split("theme_select_")[-1]
    if theme_key in THEMES:
        context.user_data['chosen_theme'] = theme_key
        chosen = THEMES[theme_key]
        text = f"🎨 *Тема выбрана:* *{chosen['name']} {chosen['X']}/{chosen['O']}*\n\nВыберите другую тему или начните игру."
        buttons = []
        for key, theme in THEMES.items():
            btn_text = f"{theme['name']} {theme['X']}/{theme['O']}"
            if key == theme_key:
                btn_text = f"✅ {btn_text}"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"theme_select_{key}")])
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
        except telegram.error.BadRequest:
            await update.effective_chat.send_message(text, parse_mode="Markdown")

async def change_theme_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки 'Сменить тему' во время игры."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    if chat_id not in games or games[chat_id].get('game_over', True):
        await query.answer("Игра не найдена или уже завершена.", show_alert=True)
        return

    # Составляем кнопки для выбора темы во время игры
    current_emojis = games[chat_id].get('theme_emojis', THEMES[DEFAULT_THEME_KEY])
    current_key = next((k for k, v in THEMES.items() if v == current_emojis), DEFAULT_THEME_KEY)

    buttons = []
    for key, theme in THEMES.items():
        btn = f"{theme['name']} {theme['X']}/{theme['O']}"
        if key == current_key:
            btn = f"🎮 {btn}"
        buttons.append([InlineKeyboardButton(btn, callback_data=f"theme_select_ingame_{key}")])
    buttons.append([InlineKeyboardButton("Назад к игре", callback_data="cancel_theme_change")])

    await query.edit_message_text(
        "🎨 *Смена темы во время игры* 🎨\n\nВыберите новую тему для текущей игры.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def select_theme_ingame_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора темы во время игры."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    theme_key = query.data.split("theme_select_ingame_")[-1]
    if chat_id not in games or theme_key not in THEMES:
        await query.answer("Некорректная тема или игра не найдена.", show_alert=True)
        return

    # Применяем выбранную тему
    games[chat_id]['theme_emojis'] = THEMES[theme_key].copy()
    # Override custom symbols for VIP users
    game_data = games[chat_id]
    for uid, sym in game_data.get('user_symbols', {}).items():
        custom = get_symbol(uid)
        if custom:
            game_data['theme_emojis'][sym] = custom

    context.user_data['chosen_theme'] = theme_key
    from handlers.game_handlers import _restore_game_message
    await query.answer(f"Тема '{THEMES[theme_key]['name']}' применена!")
    await _restore_game_message(query, context, chat_id, theme_changed=True)

async def cancel_theme_change_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки 'Назад к игре' при смене темы."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    if chat_id not in games:
        await query.answer("Игра не найдена.", show_alert=True)
        return

    from handlers.game_handlers import _restore_game_message
    await _restore_game_message(query, context, chat_id, theme_changed=False)

# Handler objects
themes_handler = CommandHandler("themes", themes_command)
select_theme_handler = CallbackQueryHandler(select_theme_callback, pattern=r"^theme_select_(?!ingame_).*")
change_theme_prompt_handler = CallbackQueryHandler(change_theme_prompt_callback, pattern=r"^change_theme_prompt$")
select_theme_ingame_handler = CallbackQueryHandler(select_theme_ingame_callback, pattern=r"^theme_select_ingame_")
cancel_theme_change_handler = CallbackQueryHandler(cancel_theme_change_callback, pattern=r"^cancel_theme_change$") 