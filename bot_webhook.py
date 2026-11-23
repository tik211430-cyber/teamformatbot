"""
Team Format Bot - Webhook version (Render FREE web service er jonno)
Polling version: bot.py (PC te chalao)
Webhook version: ei file (Render free te 24 ghonta)

Render e Web Service hisabe deploy koro, Background Worker na.
Free web service 15 min por ghumay - UptimeRobot diye 14 min por por
https://tomar-service.onrender.com/ ping dile ghumabe na.
"""
import os
import asyncio
from flask import Flask, request, jsonify

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# bot.py theke parser use korchi - eki niyom
from bot import parse_teams, format_teams

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # jemon https://teamformatbot.onrender.com/webhook
# Render nijei RENDER_EXTERNAL_URL dey, oita thakle oita use hobe
if not WEBHOOK_URL and os.environ.get("RENDER_EXTERNAL_URL"):
    WEBHOOK_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/") + "/webhook"

app = Flask(__name__)
application = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Team Format Bot\n\n"
        "Ogosalo team details pathao, ami ei niyome sajiye dibo:\n\n"
        "1. TEAM NAME : EXAMPLE1\n"
        "PLAYER NAME 1 : DSHDH\n"
        "PLAYER NAME 2 : FFJNF\n"
        "PLAYER NAME 3 : FHHF\n"
        "PLAYER NAME 4 : \n"
        "PLAYER NAME 5 : \n\n"
        "IGN / PLAYER — jekono label dilei cholbe, khali line skip hobe."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if not text.strip() or text.strip().startswith("/"):
        return
    teams = parse_teams(text)
    if not teams or all(not t["team"] and not t["players"] for t in teams):
        await update.message.reply_text(
            "Team details bujhte parlam na. Eivabe pathao:\n\n"
            "TEAM NAME : EXAMPLE1\n"
            "IGN NAME : DSHDH\n"
            "IGN : FFJNF\n"
            "PLAYER : FHHF"
        )
        return
    formatted = format_teams(teams)
    await update.message.reply_text(f"```\n{formatted}```", parse_mode="Markdown")


def build_app():
    global application
    if application is not None:
        return application
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN set koro")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return application


@app.route("/", methods=["GET"])
def health():
    # UptimeRobot ei page ta ping korbe
    return "Team Format Bot cholche", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    tg_app = build_app()
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    asyncio.run(tg_app.process_update(update))
    return jsonify({"ok": True})


@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    """Browser e https://tomar-service.onrender.com/set-webhook khulle webhook set hobe."""
    if not WEBHOOK_URL:
        return "WEBHOOK_URL / RENDER_EXTERNAL_URL set koro", 500
    tg_app = build_app()
    ok = asyncio.run(tg_app.bot.set_webhook(url=WEBHOOK_URL))
    return jsonify({"ok": ok, "webhook_url": WEBHOOK_URL})


if __name__ == "__main__":
    build_app()
    if WEBHOOK_URL:
        print(f"Webhook set korchi: {WEBHOOK_URL}")
        asyncio.run(application.bot.set_webhook(url=WEBHOOK_URL))
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
