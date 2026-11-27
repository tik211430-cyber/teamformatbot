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
import difflib
import unicodedata
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


PAYMENT_LABELS = ("bkash", "nagad", "rocket", "payment", "contact", "phone", "mobile", "number")

# Stylish font er character -> simple ASCII. NFKD nijei beshir vag
# (bold / script / fraktur / double-struck / fullwidth / circled)
# handle kore, kintu small caps, superscript ar negative-squared
# gula ke age haat e map korte hoy.
_SIMPLE_MAP = str.maketrans({
    # small caps
    "ᴀ": "a", "ʙ": "b", "ᴄ": "c", "ᴅ": "d", "ᴇ": "e", "ɢ": "g",
    "ʜ": "h", "ɪ": "i", "ᴊ": "j", "ᴋ": "k", "ʟ": "l", "ᴍ": "m",
    "ɴ": "n", "ᴏ": "o", "ᴘ": "p", "ʀ": "r", "ᴛ": "t", "ᴜ": "u",
    "ᴠ": "v", "ᴡ": "w", "ʏ": "y", "ᴢ": "z", "ᴁ": "ae", "ꜰ": "f",
    "ꜱ": "s",
    # superscript / subscript (jegula NFKD dhore na)
    "ᵃ": "a", "ᵇ": "b", "ᶜ": "c", "ᵈ": "d", "ᵉ": "e", "ᶠ": "f",
    "ᵍ": "g", "ʰ": "h", "ⁱ": "i", "ʲ": "j", "ᵏ": "k", "ˡ": "l",
    "ᵐ": "m", "ⁿ": "n", "ᵒ": "o", "ᵖ": "p", "ʳ": "r", "ˢ": "s",
    "ᵗ": "t", "ᵘ": "u", "ᵛ": "v", "ʷ": "w", "ˣ": "x", "ʸ": "y",
    "ᶻ": "z", "ₐ": "a", "ₑ": "e", "ₒ": "o", "ₓ": "x",
    # negative squared letters
    "🅰": "A", "🅱": "B", "🅲": "C", "🅳": "D", "🅴": "E", "🅵": "F",
    "🅶": "G", "🅷": "H", "🅸": "I", "🅹": "J", "🅺": "K", "🅻": "L",
    "🅼": "M", "🅽": "N", "🅾": "O", "🅿": "P", "🆀": "Q", "🆁": "R",
    "🆂": "S", "🆃": "T", "🆄": "U", "🆅": "V", "🆆": "W", "🆇": "X",
    "🆈": "Y", "🆉": "Z",
    # Hangul filler - stylish naam e space er moto use hoy
    "ㅤ": " ", "ᅠ": " ",
    # Cherokee lookalikes (Latin er moto dekhte)
    "Ꭺ": "A", "Ᏼ": "B", "Ꮯ": "C", "Ꭰ": "D", "Ꭼ": "E", "Ᏻ": "G",
    "Ꮋ": "H", "Ꭵ": "I", "Ꮶ": "K", "Ꮮ": "L", "Ꮇ": "M", "Ꮑ": "N",
    "Ꭴ": "O", "Ꮲ": "P", "Ꭱ": "R", "Ꮪ": "S", "Ꭲ": "T", "Ꮜ": "U",
    "Ꮙ": "V", "Ꮤ": "W", "Ꮍ": "Y", "Ꮓ": "Z",
    # Cyrillic homoglyphs (Latin er moto dekhte)
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H",
    "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "У": "Y",
    "Ј": "J", "Ѕ": "S", "І": "I", "Ї": "I", "Ґ": "G",
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x",
    "у": "y", "ј": "j", "ѕ": "s", "і": "i", "ї": "i", "ґ": "g",
    "к": "k", "м": "m", "н": "h", "т": "t", "в": "b", "ԁ": "d",
    "Ԑ": "E",
    # Latin extended lookalikes
    "Ɓ": "B", "ɓ": "b", "Ɔ": "O", "ɔ": "o", "Ɗ": "D", "ɗ": "d",
    "Ɛ": "E", "ɛ": "e", "Ƒ": "F", "ƒ": "f", "Ɠ": "G", "ɠ": "g",
    "Ɩ": "I", "ɩ": "i", "Ƙ": "K", "ƙ": "k", "Ɯ": "W", "ɯ": "w",
    "Ɲ": "N", "ɲ": "n", "Ɵ": "O", "ɵ": "o", "Ƥ": "P", "ƥ": "p",
    "Ʀ": "R", "Ƨ": "S", "ƨ": "s", "Ƭ": "T", "ƭ": "t", "Ʈ": "T",
    "ʈ": "t", "Ʋ": "V", "ʋ": "v", "Ƴ": "Y", "ƴ": "y", "Ƶ": "Z",
    "ƶ": "z", "ʑ": "z", "Ʒ": "E", "ʒ": "z", "ʂ": "s", "ʃ": "s",
    "Ƞ": "N", "ȵ": "n",
})


def to_simple_text(value: str) -> str:
    """Stylish / fancy font er naam ke simple text e convert kore.
    Jemon 𝐓𝐅𝐗, 𝕋𝔽𝕏, ＴＦＸ, ⓉⒻⓍ, ᴛꜰx, ꧁༺TFX༻꧂ -> TFX,
    ar Ᏼᴜɴɴʏ -> Bunny, Ɓᴀɴ—͞Ꭱᴀᴋɪʙ -> Ban Rakib.
    Shudhu ASCII letter, digit, space, -, . ar _ thake; baki
    sob sajano chinno space hoye jay ba bad jay."""
    if not value:
        return value
    text = value.translate(_SIMPLE_MAP)
    text = unicodedata.normalize("NFKD", text)
    out = []
    for ch in text:
        if unicodedata.category(ch) == "Mn":
            continue
        if ch.isascii() and (ch.isalnum() or ch in " -._"):
            out.append(ch)
        else:
            out.append(" ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _close(word: str, target: str, threshold: float = 0.7) -> bool:
    """Banan vul holeo mil khay kina - jemon 'tem' ~ 'team',
    'plaer' ~ 'player', 'nmae' ~ 'name'."""
    word = word.lower()
    if word == target:
        return True
    return difflib.SequenceMatcher(None, word, target).ratio() >= threshold


def _label_words(label: str):
    return re.findall(r'[a-z]+', label.lower())


def _is_team_label(label: str) -> bool:
    ws = _label_words(label)
    if any(_close(w, "team", 0.7) for w in ws):
        return True
    joined = "".join(ws)
    return _close(joined, "team", 0.7) or _close(joined, "teamname", 0.7)


def _is_player_label(label: str) -> bool:
    ws = _label_words(label)
    if any(_close(w, "player", 0.7) or _close(w, "ign", 0.6) for w in ws):
        return True
    joined = "".join(ws)
    return (_close(joined, "player", 0.7) or _close(joined, "playername", 0.7)
            or _close(joined, "ignname", 0.6) or _close(joined, "ign", 0.6))


def _is_name_label(label: str) -> bool:
    return any(_close(w, "name", 0.7) for w in _label_words(label))


def _strip_leading_label(line: str, targets) -> str:
    """Line er shurur label word gula (banan vul holeo) soray, value rakhe.
    Jemon 'TEM NMAE EXAMPLE1' -> 'EXAMPLE1', 'PLAER DSHDH' -> 'DSHDH'.
    Naam jodi label er cheye onek boro hoy (jemon IGNIS) ta sorano hobe na."""
    parts = line.split()
    i = 0
    while i < len(parts):
        word = re.sub(r'[^a-zA-Z]', '', parts[i]).lower()
        if not word:
            i += 1
            continue
        if word.isdigit():
            i += 1
            continue
        hit = False
        for t in targets:
            thresh = 0.6 if t == "ign" else 0.7
            if len(word) <= len(t) + 1 and _close(word, t, thresh):
                hit = True
                break
        if not hit:
            break
        i += 1
    return " ".join(parts[i:]).strip(" :-")


def is_phone_number(value: str) -> bool:
    """Shudhu ekta phone/payment number kina - jemon 01751688757.
    Naam er sathe number thakle (NFY10) eta False dibe."""
    clean = re.sub(r'[\s\-]', '', value.strip())
    if clean.startswith("+"):
        clean = clean[1:]
    return clean.isdigit() and len(clean) in (10, 11) and clean.startswith("01")


def is_payment_line(line_noprefix: str) -> bool:
    """bKash / Nagad / Rocket / contact number er line kina.
    TEAM / PLAYER / IGN thakle eta payment line na - banan vul holeo."""
    if _is_team_label(line_noprefix) or _is_player_label(line_noprefix):
        return False
    if ":" in line_noprefix:
        label = line_noprefix.split(":", 1)[0].strip()
        return any(_close(w, k, 0.7) for w in _label_words(label) for k in PAYMENT_LABELS)
    # Colon chara line - "BKASH 0175..." er moto, kintu "ROCKET X"
    # er moto naam hole skip korbo na
    low = line_noprefix.lower()
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
        # Label check sudhu colon er ager ongsho diye - value te
        # "team" / "player" thakleo vul kore team/player dhorbe na.
        # Colon na thakle pura line tai label hisebe check hobe.
        label = line_noprefix.split(":", 1)[0] if ":" in line_noprefix else line_noprefix

        # 1) TEAM NAME line - banan vul holeo (TEM / TAEM / TEEM)
        if _is_team_label(label):
            value = extract_after_colon(line_noprefix)
            if not value:
                # "TEAM NAME EXAMPLE1" - colon chara
                value = _strip_leading_label(line_noprefix, ("team", "name"))
            new_team(value)
            continue

        # 1b) bKash / Nagad / Rocket / contact number - player na, skip
        if is_payment_line(line_noprefix):
            continue

        # 2) Player line - IGN / PLAYER / NAME keyword thakle,
        # banan vul holeo (PLAER / PALYER / IGNN / NMAE)
        if _is_player_label(label) or _is_name_label(label):
            value = extract_after_colon(line_noprefix)
            if not value:
                # "IGN DSHDH" / "PLAYER FHHF" - colon chara
                value = _strip_leading_label(line_noprefix, ("ign", "player", "name"))
            if not value or is_phone_number(value):
                continue  # khali IGN 2: skip, number o player na
            if current is None:
                new_team("")
            current["players"].append(value)
            continue

        # 3) Colon ache kintu label chini na - value tai player
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
    """Parsed teams -> user er deya format e text.
    Stylish naam thakle simple text e convert kore deya hoy."""
    if not teams:
        return ""
    out_lines = []
    for i, t in enumerate(teams, start=1):
        out_lines.append(f"{i}. TEAM NAME : {to_simple_text(t['team'])}")
        players = t["players"][:5]
        for j in range(1, 6):
            name = players[j - 1] if j - 1 < len(players) else ""
            out_lines.append(f"PLAYER NAME {j} : {to_simple_text(name)}")
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
        "IGN / PLAYER — jekono label dilei cholbe, khali line skip hobe.\n\n"
        "Banan vul holeo cholbe — TEAM / PLAYER / IGN banan vul likhleo bot dhore felbe, ar amader format ei sajabe.\n\n"
        "Stylish font er naam dile simple text e convert kore dibe."
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
