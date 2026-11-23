# Render FREE te Team Format Bot chalao — Step by Step

Bot: Team Format Bot — @TeamFormatBot — t.me/TeamFormatBot
Khorocho: $0 — Free Web Service

## 1. GitHub e upload koro

1. github.com e giye New repository banao — naam `teamformatbot`
2. Ei folder er sob file upload koro: `bot.py`, `bot_webhook.py`, `requirements.txt`, `render.yaml`, `README.md`
   - GitHub web theke "uploading an existing file" diyeo hobe, git lagbe na

## 2. Render e Web Service banao (FREE)

1. render.com e account kholo (GitHub diye login korlei hobe)
2. Dashboard e **New + > Web Service**
3. GitHub repo `teamformatbot` select koro
4. Setting gulo eivabe dao:
   - **Name:** `teamformatbot`
   - **Region:** Singapore (Bangladesh er kachakachi, fast hobe)
   - **Branch:** main
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn bot_webhook:app --bind 0.0.0.0:$PORT`
   - **Instance Type:** **Free** — $0/month select koro, $7 wala na
5. **Environment Variables** e add koro:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: BotFather er deya token ta (kauke dio na)
6. **Create Web Service** dao — 2-3 minute e deploy hobe
7. Uporer dike ekta URL pabe, eirokom:
   `https://teamformatbot.onrender.com`

> Blueprint diye korte chaile: Render e **New + > Blueprint**, repo select koro — `render.yaml` theke sob setting auto nibe. Token ta tarpor Environment e dite hobe.

## 3. Webhook set koro (1 bar)

Deploy sesh hole browser e jao:
```
https://teamformatbot.onrender.com/set-webhook
```
`{"ok": true}` dekhale webhook set hoye geche.

Tarpor Telegram e @TeamFormatBot khule `/start` dao, ar ogosalo team details pathao — bot sajiye dibe.

## 4. Bot ke ghumate dio na — UptimeRobot (FREE)

Free web service 15 minute kono traffic na ashle ghumiye jay. Tai:

1. uptimerobot.com e free account kholo
2. **Add New Monitor**
   - Monitor Type: HTTP(s)
   - Friendly Name: `TeamFormatBot`
   - URL: `https://teamformatbot.onrender.com/`
   - Monitoring Interval: **5 Minutes**
3. Save dao

Eita 5 minute por por ping dibe, bot ar ghumabe na.

## 5. Test koro

Telegram e @TeamFormatBot e pathao:
```
TEAM NAME : EXAMPLE1
IGN NAME : DSHDH
IGN 2:
IGN :FFJNF
PLAYER :FHHF
```

Bot dibe:
```
1. TEAM NAME : EXAMPLE1
PLAYER NAME 1 : DSHDH
PLAYER NAME 2 : FFJNF
PLAYER NAME 3 : FHHF
PLAYER NAME 4 : 
PLAYER NAME 5 : 
```

## Somossa hole

- Bot reply dey na: Render dashboard e Logs dekho, ar `/set-webhook` abar kholo
- Deploy fail: Build Command / Start Command uporer moto ache kina dekho, Instance Type Free kina dekho
- Token vul: BotFather e `/token` diye token abar niye Render e update koro, tarpor Manual Deploy > Deploy latest commit dao
- Token kauke dio na, GitHub e token wala file upload koro na

## PC te chalate chaile (alternative)

```
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN='tomar-token'
python bot.py
```
