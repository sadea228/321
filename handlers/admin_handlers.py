"""
Handlers for admin commands: reset, ban, unban, chat stats
"""
import telegram
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from config import logger
from game_state import games, banned_users, chat_stats
from vip import is_vip_by_username, VIP_ICON, is_vip

async def reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if update.effective_user.username != 'sadea12' and not is_vip(user_id):
        await update.message.reply_text('⛔ Только владелец или VIP могут использовать эту команду.')
        return
    chat_id = update.effective_chat.id
    if chat_id in games:
        del games[chat_id]
        await update.message.reply_text('♻️ Игра в этом чате сброшена.')
        logger.info(f'Reset game in chat {chat_id}')
    else:
        await update.message.reply_text('В этом чате нет активной игры.')

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if update.effective_user.username != 'sadea12' and not is_vip(user_id):
        await update.message.reply_text('⛔ Только владелец или VIP могут использовать эту команду.')
        return
    # Поддержка бана по ответу на сообщение
    if update.message.reply_to_message:
        user_to_ban = update.message.reply_to_message.from_user
        target = str(user_to_ban.id)
    elif context.args:
        target = context.args[0].lstrip('@')
    else:
        await update.message.reply_text('Использование: /ban <@username или user_id> или ответ на сообщение пользователя')
        return
    banned_users.add(target)
    await update.message.reply_text(f'Пользователь {target} забанен.')
    logger.info(f'User {target} banned')

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if update.effective_user.username != 'sadea12' and not is_vip(user_id):
        await update.message.reply_text('⛔ Только владелец или VIP могут использовать эту команду.')
        return
    # Поддержка разбанивания по ответу на сообщение
    if update.message.reply_to_message:
        user_to_unban = update.message.reply_to_message.from_user
        target = str(user_to_unban.id)
    elif context.args:
        target = context.args[0].lstrip('@')
    else:
        await update.message.reply_text('Использование: /unban <@username или user_id> или ответ на сообщение пользователя')
        return
    if target in banned_users:
        banned_users.remove(target)
        await update.message.reply_text(f'Пользователь {target} разбанен.')
        logger.info(f'User {target} unbanned')
    else:
        await update.message.reply_text(f'Пользователь {target} не был забанен.')

async def chat_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.username != 'sadea12':
        await update.message.reply_text('⛔ Только владелец может использовать эту команду.')
        return
    chat_id = update.effective_chat.id
    stats = chat_stats.get(chat_id)
    if not stats:
        await update.message.reply_text('В этом чате нет статистики.')
        return
    text = [f'📊 Статистика для чата {chat_id}:']
    text.append(f"Всего игр: {stats.get('games', 0)}")
    text.append(f"Побед: {stats.get('wins', 0)}")
    text.append(f"Ничьих: {stats.get('draws', 0)}")
    top = stats.get('top_players', {})
    if top:
        text.append('Топ по победам:')
        for user, count in sorted(top.items(), key=lambda x: -x[1]):
            vip_marker = VIP_ICON if is_vip_by_username(user) else ""
            text.append(f"- {user}{vip_marker}: {count}")
    await update.message.reply_text("\n".join(text))

# Handler objects
reset_game_handler = CommandHandler('resetgame', reset_game)
reset_handler = CommandHandler('reset', reset_game)
ban_user_handler = CommandHandler('ban', ban_user)
unban_user_handler = CommandHandler('unban', unban_user)
chat_stats_handler = CommandHandler('chatstats', chat_stats_command) 