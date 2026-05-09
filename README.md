# TNPSC Daily Current Affairs Bot

Automated Telegram bot that generates daily TNPSC/TNUSRB current affairs in Tamil and sends to all channels.

## Features
- Collects yesterday's news using TinyFish Search & Fetch API
- Generates structured Tamil content using Groq AI (Llama 3.3 70B)
- Sends .txt file to all 96 channels daily at 7 AM IST
- Manual trigger via /generate command
- Health check endpoint for UptimeRobot

## Deployment on Render

### Step 1: Upload to GitHub
1. Create a new repository on GitHub
2. Upload these files: `app.py`, `requirements.txt`, `Procfile`

### Step 2: Deploy on Render
1. Go to render.com → New → Web Service
2. Connect your GitHub repo
3. Settings:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance Type: Free

### Step 3: Set Environment Variables (in Render dashboard)
Add these in Render → Your Service → Environment:

| Variable | Value |
|----------|-------|
| BOT_TOKEN | Your Telegram bot token |
| TINYFISH_API_KEY | Your TinyFish API key |
| GROQ_API_KEY | Your Groq API key |
| OWNER_ID | Your Telegram user ID |

### Step 4: Set Webhook
After deployment, open this URL in browser:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_RENDER_URL>/<YOUR_BOT_TOKEN>
```

### Step 5: Keep Alive (UptimeRobot)
1. Go to uptimerobot.com
2. Add HTTP monitor for your Render URL
3. Set interval to 5 minutes

## Bot Commands
- `/generate` - Generate & send current affairs now
- `/status` - Check bot status
- `/help` - Show help message
