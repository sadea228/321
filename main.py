import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, JobQueue, ContextTypes

from config import TOKEN, logger
import handlers.game_handlers as game_handlers
import handlers.theme_handlers as theme_handlers
import handlers.admin_handlers as admin_handlers
import handlers.admin_panel_handlers as admin_panel_handlers
import handlers.ai_handlers as ai_handlers
import handlers.vip_handlers as vip_handlers


async def main() -> None:
    if not TOKEN:
        logger.critical("TOKEN не задан")
        return

    job_queue = JobQueue()
    app = Application.builder().token(TOKEN).job_queue(job_queue).build()

    # Регистрируем обработчики
    app.add_handler(game_handlers.start_handler)
    app.add_handler(game_handlers.new_game_handler)
    app.add_handler(game_handlers.button_click_handler)
    app.add_handler(theme_handlers.themes_handler)
    app.add_handler(theme_handlers.select_theme_handler)
    app.add_handler(theme_handlers.change_theme_prompt_handler)
    app.add_handler(theme_handlers.select_theme_ingame_handler)
    app.add_handler(theme_handlers.cancel_theme_change_handler)
    app.add_handler(admin_handlers.reset_game_handler)
    app.add_handler(admin_handlers.reset_handler)
    app.add_handler(admin_handlers.ban_user_handler)
    app.add_handler(admin_handlers.unban_user_handler)
    app.add_handler(admin_handlers.chat_stats_handler)
    app.add_handler(ai_handlers.play_ai_handler)
    app.add_handler(vip_handlers.vip_handler)
    app.add_handler(vip_handlers.setavatar_handler)
    app.add_handler(vip_handlers.signature_handler)
    app.add_handler(vip_handlers.setvip_handler)
    app.add_handler(vip_handlers.removevip_handler)
    app.add_handler(vip_handlers.setsymbol_handler)
    app.add_handler(vip_handlers.viphelp_handler)
    app.add_handler(admin_panel_handlers.admin_panel_handler)
    app.add_handler(admin_panel_handlers.admin_callback_handler)

    # Регистрируем команды
    commands = [
        BotCommand("start", "👋 Запустить бота"),
        BotCommand("newgame", "🎲 Начать новую игру"),
        BotCommand("play_ai", "🤖 Играть против ИИ"),
        BotCommand("themes", "🎨 Выбрать тему"),
        BotCommand("resetgame", "♻️ Сбросить игру"),
        BotCommand("reset", "♻️ Сбросить игру"),
        BotCommand("ban", "🚫 Бан пользователя"),
        BotCommand("unban", "✅ Разбан пользователя"),
        BotCommand("chatstats", "📊 Статистика по чату"),
        BotCommand("vip", "💎 Получить VIP-подписку"),
        BotCommand("setavatar", "👤 Установить аватар VIP"),
        BotCommand("setsignature", "✍️ Установить подпись VIP"),
        BotCommand("setsymbol", "🎭 Установить символ VIP"),
        BotCommand("viphelp", "💡 Список команд VIP"),
        BotCommand("setvip", "👑 Выдать VIP-подписку"),
        BotCommand("removevip", "🔴 Забрать VIP-подписку"),
        BotCommand("admin", "👑 Открыть админ‑панель"),
    ]

    await app.initialize()
    await app.bot.set_my_commands(commands)
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Глобальный обработчик ошибок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.exception("Произошла ошибка при обработке обновления", exc_info=context.error)
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❗️ Произошла внутренняя ошибка. Пожалуйста, попробуйте позже."
                )
            except Exception:
                pass

    app.add_error_handler(error_handler)

    await app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановлено вручную")
