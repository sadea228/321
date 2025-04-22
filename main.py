import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response
from http import HTTPStatus

from telegram import Update, BotCommand
from telegram.ext import Application, JobQueue, ContextTypes

from config import TOKEN, WEBHOOK_ENDPOINT_URL, WEBHOOK_PATH, PORT, logger
import handlers.game_handlers as game_handlers
import handlers.theme_handlers as theme_handlers
import handlers.admin_handlers as admin_handlers
import handlers.admin_panel_handlers as admin_panel_handlers
import handlers.ai_handlers as ai_handlers
import handlers.vip_handlers as vip_handlers

fastapi_app = FastAPI()

async def handle_telegram_update(request: Request, application: Application):
    body = await request.json()
    update = Update.de_json(body, application.bot)
    await application.process_update(update)
    return Response(status_code=HTTPStatus.OK)

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

    # Вебхук
    if WEBHOOK_ENDPOINT_URL:
        await app.bot.set_webhook(url=WEBHOOK_ENDPOINT_URL, allowed_updates=Update.ALL_TYPES)
        async def webhook(request: Request):
            return await handle_telegram_update(request, app)
        fastapi_app.add_api_route(WEBHOOK_PATH, webhook, methods=["POST"])

    # Глобальный обработчик ошибок для логирования и уведомления пользователя
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.exception("Произошла ошибка при обработке обновления", exc_info=context.error)
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text("❗️ Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.")
            except Exception:
                pass
    app.add_error_handler(error_handler)

    # Запуск сервера
    config = uvicorn.Config(app=fastapi_app, host="0.0.0.0", port=PORT)
    server = uvicorn.Server(config)
    await app.start()
    await server.serve()
    await app.stop()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановлено вручную") 