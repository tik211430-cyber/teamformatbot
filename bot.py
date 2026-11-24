"""
Triple Strike - Team Format Bot
Ogosalo team details dile ek niyome sajiye dibe.

Format:
1. TEAM NAME : EXAMPLE1
PLAYER NAME 1 : DSHDH
PLAYER NAME 2 : FFJNF
PLAYER NAME 3 : FHHF
PLAYER NAME 4 :
PLAYER NAME 5 :

Rules:
- TEAM NAME dekhlei notun team shuru
- IGN, IGN NAME, IGN 2, PLAYER, PLAYER NAME sobai player
- Khali value skip hobe
- Sob somoy 5 ta player slot thakbe
- Ek message e jotogulo team dibe, 1, 2, 3 kore number hobe
"""

import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


PAYMENT_LABELS = ("bkash", "nagad", "rocket", "payment", "contact", "phone", "mobile", "number")


def is_phone_number(value: str) -> bool:
    """Shudhu ekta phone/payment number kina - jemon 01751688757.
    Naam er sathe number thakle (NFY10) eta False dibe."""
    clean = re.sub(r'[\s\-]', '', value.strip())
    if clean.startswith("+"):
        clean = clean[1:]
    return clean.isdigit() and len(clean) in (10, 11) and clean.startswith("01")


def is_payment_line(line_noprefix: str) -> bool:
    """bKash / Nagad / Rocket / contact number er line kina.
    TEAM / PLAYER / IGN thakle eta payment line na."""
    low = line_noprefix.lower()
    if any(k in low for k in ("team", "player", "ign")):
        return False
    if ":" in line_noprefix:
        label = low.split(":", 1)[0].strip()
        return any(k in label for k in PAYMENT_LABELS)
    # Colon chara line - "BKASH 0175..." er moto, kintu "ROCKET X"
    # er moto naam hole skip korbo na
    for k in ("bkash", "nagad", "rocket", "payment", "contact", "phone", "mobile"):
        if low.startswith(k):
            rest = low[len(k):].strip()
            return is_phone_number(rest) or not rest
    return is_phone_number(line_noprefix)


def clean_value(text: str) -> str:
    """Colon er porer value clean kore, leading number/dot soray."""
    text = text.strip()
    # "1. TEAM NAME : X" er moto leading "1." sorano
    text = re.sub(r'^\d+\s*[\.\)]\s*', '', text)
    return text.strip()


def extract_after_colon(line: str) -> str:
    if ":" in line:
        return clean_value(line.split(":", 1)[1])
    return ""


def parse_teams(text: str):
    """Ogosalo text -> [{'team': '...', 'players': [...]}, ...]"""
    teams = []
    current = None

    def new_team(name: str):
        nonlocal current
        current = {"team": name, "players": []}
        teams.append(current)

    lines = text.splitlines()

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        low = line.lower()
        # leading "1." / "2)" sorano check er jonno
        line_noprefix = re.sub(r'^\d+\s*[\.\)]\s*', '', line).strip()
        low_noprefix = line_noprefix.lower()

        # 1) TEAM NAME line
        if "team" in low_noprefix:
            value = extract_after_colon(line_noprefix)
            if not value:
                # "TEAM NAME EXAMPLE1" - colon chara
                value = re.sub(r'(?i)team\s*name\s*', '', line_noprefix).strip()
            new_team(value)
            continue

        # 1b) bKash / Nagad / Rocket / contact number - player na, skip
        if is_payment_line(line_noprefix):
            continue

        # 2) Player line - IGN / PLAYER / NAME keyword thakle
        if any(k in low_noprefix for k in ["ign", "player"]):
            value = extract_after_colon(line_noprefix)
            if not value:
                # "IGN DSHDH" / "PLAYER FHHF" - colon chara
                value = re.sub(r'(?i)^(ign|player)(\s*name)?\s*\d*\s*[:\-]?\s*', '', line_noprefix).strip()
            if not value or is_phone_number(value):
                continue  # khali IGN 2: skip, number o player na
            if current is None:
                new_team("")
            current["players"].append(value)
            continue

        # 3) "NAME : X" - shudhu NAME lekha thakle player dhorbo
        if re.match(r'(?i)^name\s*\d*\s*:', line_noprefix):
            value = extract_after_colon(line_noprefix)
            if value and not is_phone_number(value):
                if current is None:
                    new_team("")
                current["players"].append(value)
            continue

        # 4) Colon ache kintu label chini na - value tai player
        if ":" in line_noprefix:
            value = extract_after_colon(line_noprefix)
            if value and not is_phone_number(value):
                if current is None:
                    new_team("")
                current["players"].append(value)
            continue

        # 5) Colon nai, label nai - shudhu ekta naam
        # Team nai -> team name, team ache ar player 5 er kom -> player
        # Shudhu number hole oita player na, skip
        if is_phone_number(line_noprefix):
            continue
        if current is None:
            new_team(line_noprefix)
        elif len(current["players"]) < 5:
            current["players"].append(line_noprefix)
        else:
            new_team(line_noprefix)

    return teams


def format_teams(teams):
    """Parsed teams -> user er deya format e text."""
    if not teams:
        return ""
    out_lines = []
    for i, t in enumerate(teams, start=1):
        out_lines.append(f"{i}. TEAM NAME : {t['team']}")
        players = t["players"][:5]
        for j in range(1, 6):
            name = players[j - 1] if j - 1 < len(players) else ""
            out_lines.append(f"PLAYER NAME {j} : {name}")
        out_lines.append("")  # team er majhe khali line
    return "\n".join(out_lines).rstrip() + "\n"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Triple Strike Team Format Bot\n\n"
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
    if not text.strip():
        return
    if text.strip().startswith("/"):
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
    # Plain text - upore kono cinho lagbe na
    await update.message.reply_text(formatted)


def main():
    if not TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN set koro. Example: export TELEGRAM_BOT_TOKEN='123456:ABC...'")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot cholche... Telegram e /start dao.")
    app.run_polling()


if __name__ == "__main__":
    main()
