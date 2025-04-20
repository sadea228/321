from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import logger
from bot_state import get_all_chats
from vip import vip_users, subscriptions, vip_user_map

DEFAULT_BROADCAST_TEXT = (
    "🎉 Привет! Это CrackNolikBot с важной новостью! 🎉\n\n"
    "💎 У нас появилась VIP‑подписка! Она дарит:\n"
    "  • Эксклюзивные темы и эмодзи  \n"
    "  • Собственный аватар и персональную подпись в начале партии  \n"
    "  • Приоритетную обработку запросов боту  \n"
    "  • Дополнительные режимы игры и статистику  \n"
    "  • Еженедельные бонусы и акции  \n\n"
    "👉 Чтобы стать VIP, просто введите команду:/vip\n\n"
    "Оформление происходит мгновенно через крипто‑платеж в USDT.  \n"
    "Не упустите шанс выделиться и получить максимум от игры!\n\n"
    "Спасибо, что вы с нами! 🚀"
)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает админ‑панель в личном чате"""
    # Доступ только владельцу
    if update.effective_user.username != 'sadea12':
        await update.message.reply_text('⛔ Только владелец может использовать админ‑панель.')
        return
    # Только в личном чате
    if update.effective_chat.type != 'private':
        await update.message.reply_text('ℹ️ Админ‑панель доступна только в личном чате с ботом.')
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('📬 Рассылка', callback_data='admin_broadcast')],
        [InlineKeyboardButton('💎 Статус VIP', callback_data='admin_vip_status')]
    ])
    await update.message.reply_text('👑 Панель администратора:', reply_markup=keyboard)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий в админ‑панели"""
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'admin_broadcast':
        # Отправляем рассылку с текстом по умолчанию
        chats = get_all_chats()
        count = 0
        for chat_id in chats:
            try:
                await context.bot.send_message(chat_id=chat_id, text=DEFAULT_BROADCAST_TEXT)
                count += 1
            except Exception as e:
                logger.warning(f"Не удалось отправить в чат {chat_id}: {e}")
        await query.edit_message_text(f'✅ Рассылка отправлена в {count} чатов.')
        return
    elif data == 'admin_vip_status':
        # Формируем статус VIP
        lines = ['📊 Статус VIP:']
        for user_id in vip_users:
            start = subscriptions.get(user_id)
            name = vip_user_map.get(user_id, str(user_id))
            ts = start.strftime('%Y-%m-%d %H:%M:%S') if start else '—'
            lines.append(f"- {name}: {ts}")
        text = '\n'.join(lines)
        await query.edit_message_text(text)

# Handler objects
admin_panel_handler = CommandHandler('admin', admin_command)
admin_callback_handler = CallbackQueryHandler(admin_callback, pattern=r'^admin_') 