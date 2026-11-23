# Triple Strike - Team Format Bot

Ogosalo team details dile ek niyome sajiye dibe.

## Bot ki korbe

Input (ogosalo):
```
TEAM NAME : EXAMPLE1
IGN NAME : DSHDH
IGN 2:
IGN :FFJNF
PLAYER :FHHF
```

Output (sajano):
```
1. TEAM NAME : EXAMPLE1
PLAYER NAME 1 : DSHDH
PLAYER NAME 2 : FFJNF
PLAYER NAME 3 : FHHF
PLAYER NAME 4 : 
PLAYER NAME 5 : 
```

Niyom:
- `TEAM NAME` dekhlei notun team
- `IGN`, `IGN NAME`, `PLAYER`, `PLAYER NAME` sobai player
- Khali line skip hobe
- Sob somoy 5 ta player slot thakbe
- Ek message e onek team dile 1, 2, 3 kore number hobe

## 1. Bot create koro - BotFather (2 min)

1. Telegram e `@BotFather` kholo
2. `/newbot` pathao
3. Bot er naam dao - jemon `Triple Strike Team Bot`
4. Username dao - jemon `triplestriketeambot` (sheshe `bot` thakte hobe, unique hote hobe)
5. BotFather ekta token dibe, eirokom: `123456789:ABCdef...`
   Token ta kauke dio na, sudhu bot chalate lagbe.

## 2. Bot chalao - PC te

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN='tomar-token-ekhane'
python bot.py
```

Windows hole:
```bash
pip install -r requirements.txt
set TELEGRAM_BOT_TOKEN=tomar-token-ekhane
python bot.py
```

## 3. Bot chalao - Render FREE te (24 ghonta cholbe)

PC bondho korle bot bondho hoye jabe. Free te 24 ghonta chalate `DEPLOY_RENDER_FREE.md` dekho — webhook version (`bot_webhook.py`) Render Free Web Service e deploy koro, Background Worker na (worker free na, $7/month).

Songkhepe:
1. Ei folder ta GitHub e upload koro
2. render.com e New > Web Service (Free)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn bot_webhook:app --bind 0.0.0.0:$PORT`
5. Environment Variable: `TELEGRAM_BOT_TOKEN` = tomar token
6. Deploy sesh hole `https://tomar-service.onrender.com/set-webhook` kholo
7. UptimeRobot e 5 min por por `https://tomar-service.onrender.com/` ping dao, tahole bot ghumabe na

## Test koro

Telegram e bot ta khule `/start` dao, tarpor ogosalo details pathao. Bot sajano copy ta dibe.
