# handlers/vip_handlers.py

import os
import asyncio
from telegram import Update, Message
from telegram.ext import ContextTypes, CommandHandler
from aiosend import CryptoPay
from aiosend.types import Invoice
from vip import add_vip, set_avatar, get_avatar, is_vip, set_signature, get_signature
from config import logger

# Инициализация CryptoPay
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
if not CRYPTO_TOKEN:
    logger.error("Необходимо установить переменную окружения CRYPTO_TOKEN для CryptoPay!")
cp = CryptoPay(CRYPTO_TOKEN)

async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Генерирует счет для VIP-подписки"""
    amount = 1  # цена подписки в USDT
    asset = "USDT"
    invoice = await cp.create_invoice(amount, asset)
    await update.message.reply_text(
        f"💎 Оплатите VIP-подписку ({amount} {asset}): {invoice.mini_app_invoice_url}"
    )
    invoice.poll(message=update.message)

@cp.invoice_polling()
async def vip_payment_received(invoice: Invoice, message: Message) -> None:
    """Обработчик получения платежа"""
    user_id = message.from_user.id
    username = message.from_user.username
    add_vip(user_id, username)
    await message.reply_text(
        "🎉 Оплата получена! Вы стали VIP-подписчиком! 🎉"
    )

async def set_avatar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Позволяет VIP-пользователю установить свой аватар"""
    user_id = update.effective_user.id
    if not is_vip(user_id):
        await update.message.reply_text("⛔ Только VIP пользователи могут менять аватар.")
        return
    if not context.args:
        await update.message.reply_text("Использование: /setavatar <emoji>")
        return
    emoji = context.args[0]
    set_avatar(user_id, emoji)
    await update.message.reply_text(f"✅ Ваш аватар установлен: {emoji}")

async def set_signature_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Позволяет VIP-пользователю установить свою подпись для приветствия"""
    user_id = update.effective_user.id
    if not is_vip(user_id):
        await update.message.reply_text("⛔ Только VIP пользователи могут устанавливать подпись.")
        return
    if not context.args:
        await update.message.reply_text("Использование: /setsignature <текст подписи>")
        return
    text = " ".join(context.args)
    set_signature(user_id, text)
    await update.message.reply_text(f"✅ Ваша подпись установлена: {text}")

async def setvip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Позволяет владельцу sadea12 выдавать VIP-подписку любому пользователю"""
    # Проверяем право доступа
    if update.effective_user.username != 'sadea12':
        await update.message.reply_text('⛔ Только владелец может выдавать VIP!')
        return
    # Определяем целевого пользователя
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        user_id = target_user.id
        username = target_user.username
    elif context.args and context.args[0].isdigit():
        user_id = int(context.args[0])
        username = None
        try:
            chat_id = update.effective_chat.id
            member = await context.bot.get_chat_member(chat_id, user_id)
            username = member.user.username
        except Exception:
            pass
    else:
        await update.message.reply_text('Использование: /setvip <user_id> или ответом на сообщение')
        return
    # Выдаем VIP
    add_vip(user_id, username)
    target_name = username or user_id
    await update.message.reply_text(f'🎉 Пользователь {target_name} теперь VIP!')

# Handler objects
vip_handler = CommandHandler("vip", vip_command)
setavatar_handler = CommandHandler("setavatar", set_avatar_command)
signature_handler = CommandHandler("setsignature", set_signature_command)
setvip_handler = CommandHandler("setvip", setvip_command) 