"""
Team Format Bot - Webhook version (Render FREE web service er jonno)
Polling version: bot.py (PC te chalao)
Webhook version: ei file (Render free te 24 ghonta)

Render e Web Service hisabe deploy koro, Background Worker na.
Free web service 15 min por ghumay - UptimeRobot diye 5 min por por
https://tomar-service.onrender.com/ ping dile ghumabe na.

NOTE: python-telegram-bot er Application ke Flask er prottek request e
asyncio.run() diye chalano jay na - ditiyo bar "Event loop is closed"
error hoy. Tai ekhane Telegram API te sorasori urllib diye kotha bola
hoy, kono asyncio / Application nei. Parser bot.py thekei ase.
"""
import json
import os
import urllib.request
import urllib.error

from flask import Flask, request, jsonify

# bot.py theke parser use korchi - eki niyom
from bot import parse_teams, format_teams

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # jemon https://teamformatbot.onrender.com/webhook
# Render nijei RENDER_EXTERNAL_URL dey, oita thakle oita use hobe
if not WEBHOOK_URL and os.environ.get("RENDER_EXTERNAL_URL"):
    WEBHOOK_URL = os.environ["RENDER_EXTERNAL_URL"].rstrip("/") + "/webhook"

app = Flask(__name__)

START_TEXT = (
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


def tg_call(method, payload):
    """Telegram Bot API te ekta call. Timeout holeo exception raise kore na,
    bodle (False, error-text) dey, jate webhook 200 dite pare."""
    if not TOKEN:
        return False, "TELEGRAM_BOT_TOKEN set koro"
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return bool(body.get("ok")), body
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"description": str(e)}
        print(f"Telegram {method} HTTP {e.code}: {body}")
        return False, body
    except Exception as e:
        print(f"Telegram {method} error: {e!r}")
        return False, str(e)


def send_message(chat_id, text):
    return tg_call("sendMessage", {"chat_id": chat_id, "text": text})


@app.route("/", methods=["GET"])
def health():
    # UptimeRobot ei page ta ping korbe
    return "Team Format Bot cholche", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or ""
    if not chat_id or not text.strip():
        return jsonify({"ok": True})
    if text.strip().startswith("/"):
        # /start, /help - onno command eo start text
        send_message(chat_id, START_TEXT)
        return jsonify({"ok": True})
    teams = parse_teams(text)
    if not teams or all(not t["team"] and not t["players"] for t in teams):
        send_message(
            chat_id,
            "Team details bujhte parlam na. Eivabe pathao:\n\n"
            "TEAM NAME : EXAMPLE1\n"
            "IGN NAME : DSHDH\n"
            "IGN : FFJNF\n"
            "PLAYER : FHHF",
        )
        return jsonify({"ok": True})
    formatted = format_teams(teams)
    send_message(chat_id, f"```\n{formatted}```")
    return jsonify({"ok": True})


@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    """Browser e https://tomar-service.onrender.com/set-webhook khulle webhook set hobe."""
    if not WEBHOOK_URL:
        return "WEBHOOK_URL / RENDER_EXTERNAL_URL set koro", 500
    ok, result = tg_call("setWebhook", {"url": WEBHOOK_URL})
    if not ok:
        return jsonify({"ok": False, "webhook_url": WEBHOOK_URL, "error": result}), 500
    return jsonify({"ok": True, "webhook_url": WEBHOOK_URL})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
