import os
import json
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# Environment Variables (set in Render dashboard, NOT in code)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TINYFISH_API_KEY = os.environ.get("TINYFISH_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OWNER_ID = int(os.environ.get("OWNER_ID", "5929125456"))

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# All 96 channels
PUBLIC_CHANNELS = [
    '@FULL_MOVIE_DATABASE', '@Eternals_disneyplus', '@freeonlinetestse', '@TNPSCASPIRANTTHOZAN',
    '@hsjvdodmndk', '@maduraipakkam', '@Mr_kn_TG', '@Sundar_Jayanth', '@Tnpsc_mattum_pothumaa',
    '@pngconverter_bot', '@kalamtnpsccoachingcentre', '@dghkkjffvh', '@TNPSC_Mattum_Pothuma',
    '@kannavu', '@Tnusrb_Police_Si_Exam_Tamil', '@pyro_userbot', '@TeleGiG_EmployBot',
    '@annamalai_k', '@zohoexamdiscussiongroup', '@EETYjobs', '@AutoMobileOpenBookAnswers',
    '@TN_BJP_it_wing', '@infomesfc', '@Vivek_ice_men', '@Tnpsc_Free_Test_Pdf',
    '@Maxton_Hall_Tamil_Download', '@santhoshmanitnpsc', '@mba_a22', '@Employment_News_Paper_Tamil',
    '@Under_Paris_Tamil_Download', '@Gutar_Gu_Tamil_Download', '@Arun_sk', '@Tnpsc_Group04',
    '@nivisha199807', '@sankartnpsctestbatch', '@tamilsaraltech', '@preparetocrack',
    '@tnpscgeneralenglishaspirant', '@TNPSCTNUSRBDQUIZ', '@tnpsc0fficial', '@virutchamtnpsc',
    '@TNPSC_MATTUM_POTHUMAAA', '@Jobs_in_Chennai_Local', '@draramadoss', '@AIADMKITWINGOFL',
    '@tnpscgeneralenglishgroup', '@inforVERSE', '@Engineering_Ask', '@tnpscfreequizz',
    '@prepforfuture', '@maduraiyar', '@jrtnpsc', '@GLl4_VKVfPLaVCoygF71iw',
    '@Test_Serious', '@neovao', '@NirmalChristo_CWC', '@SavukkuOfficial',
    '@tnpscallstudy', '@tnpscofficiall', '@seerudai', '@tamilnadupolice24',
    '@manithaneyamiasacadamy', '@ai_tnpsc', '@tgpsc2024', '@KMF_TNPSCAcademy',
    '@smartworktnpsc', '@kalvi_vaagai', '@target125125TNPSC', '@thirumaofficial',
    '@ARMTNPSC', '@tn_psc_usrb_fusrb', '@employmenttamil'
]

PRIVATE_CHANNELS = [
    -1001655625927, -1001834093615, -1001837437389, -1001887708386, -1001885403640,
    -1002087326522, -1002082356851, -1002119132551, -1002186166125, -1002179061654,
    -1002173248385, -1002206005285, -1002203648737, -1002190957882, -1002211468849,
    -1002210363948, -1002208929554, -1002234444004, -1002224157160, -1002223231366,
    -1002244166756, -1002243560534, -1002240177506, -1002310768925
]

ALL_CHANNELS = PUBLIC_CHANNELS + PRIVATE_CHANNELS


def tinyfish_search(query, num_results=10):
    """Search using TinyFish Search API"""
    url = "https://api.tinyfish.ai/v1/search"
    headers = {
        "Authorization": f"Bearer {TINYFISH_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "num_results": num_results
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"TinyFish Search error: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"TinyFish Search exception: {e}")
        return None


def tinyfish_fetch(url_to_fetch):
    """Fetch URL content using TinyFish Fetch API"""
    url = "https://api.tinyfish.ai/v1/fetch"
    headers = {
        "Authorization": f"Bearer {TINYFISH_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url_to_fetch,
        "format": "markdown"
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"TinyFish Fetch error: {resp.status_code}")
            return None
    except Exception as e:
        print(f"TinyFish Fetch exception: {e}")
        return None


def groq_generate(prompt):
    """Generate Tamil content using Groq API with Llama 3.3 70B"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert Tamil content writer specializing in TNPSC and TNUSRB competitive exam current affairs. Write in clear, simple, grammatically correct Tamil. Never use English words when Tamil equivalents exist. Ensure zero spelling mistakes."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 8000
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            print(f"Groq error: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Groq exception: {e}")
        return None


def collect_news():
    """Collect yesterday's news using TinyFish Search API"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    search_queries = [
        f"India national news {yesterday} important events",
        f"Tamil Nadu news {yesterday} government policy",
        f"international news {yesterday} important events",
        f"India economy science technology news {yesterday}",
        f"TNPSC current affairs {yesterday}",
        f"Tamil Nadu state news today sports awards"
    ]
    
    all_results = []
    for query in search_queries:
        results = tinyfish_search(query, num_results=5)
        if results and "results" in results:
            all_results.extend(results["results"])
        time.sleep(0.5)
    
    # Fetch content from top results
    news_content = []
    seen_urls = set()
    for result in all_results[:15]:
        url = result.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        fetched = tinyfish_fetch(url)
        if fetched and fetched.get("content"):
            news_content.append({
                "title": result.get("title", ""),
                "url": url,
                "content": fetched["content"][:2000]  # Limit content length
            })
        time.sleep(0.3)
    
    return news_content


def generate_current_affairs():
    """Generate the full current affairs markdown document"""
    yesterday = (datetime.now() - timedelta(days=1))
    date_str = yesterday.strftime("%d.%m.%Y")
    
    print(f"Collecting news for {date_str}...")
    news_content = collect_news()
    
    # Prepare news summary for Groq
    news_summary = ""
    for i, item in enumerate(news_content[:12], 1):
        news_summary += f"\n{i}. Title: {item['title']}\nContent: {item['content'][:500]}\n"
    
    # Generate Tamil content using Groq
    prompt = f"""Based on the following news from {date_str}, create a comprehensive TNPSC/TNUSRB competitive exam current affairs document in Tamil.

NEWS DATA:
{news_summary}

STRICT REQUIREMENTS:
1. Write ENTIRELY in Tamil language (use Tamil script only)
2. The document must be exactly 6 pages worth of content
3. Structure it with these sections:
   - 📌 தேசிய நிகழ்வுகள் (National Events) - 4-5 items
   - 🌍 சர்வதேச நிகழ்வுகள் (International Events) - 3-4 items
   - 🏛️ தமிழ்நாடு செய்திகள் (Tamil Nadu News) - 4-5 items
   - 💰 பொருளாதாரம் (Economy) - 2-3 items
   - 🔬 அறிவியல் & தொழில்நுட்பம் (Science & Technology) - 2-3 items
   - 🏆 விளையாட்டு & விருதுகள் (Sports & Awards) - 2-3 items
   - ❓ வினாடி வினா (Quiz) - 10 multiple choice questions with answers

4. For each news item, provide:
   - A clear headline in Tamil
   - 2-3 lines of explanation
   - Key facts that may appear in exams

5. Quiz questions must be based on the news items above with 4 options (அ, ஆ, இ, ஈ) and correct answer

6. Use these emoji markers: 📌 🌍 🏛️ 💰 🔬 🏆 ❓ ✅ 📚 💡
7. DO NOT use any English words
8. Ensure ZERO spelling mistakes in Tamil
9. Make content exam-focused and informative"""

    print("Generating Tamil content...")
    content = groq_generate(prompt)
    
    if not content:
        return None
    
    # Build the final markdown document
    title = f"நடப்பு கால நிகழ்வுகள் - {date_str}"
    
    document = f"""{'='*50}
📚 {title}
{'='*50}

{content}

{'='*50}
📖 கல்வி உபகரண விற்பனை நிலையம்
🔗 https://employmenttamil.in/shop/
{'='*50}

© Employment TAMIL
நடப்பு கால நிகழ்வுகள் - தினசரி புதுப்பிப்பு
{'='*50}
"""
    
    return title, document


def send_document_to_channels(title, content):
    """Send the .txt file to all channels"""
    yesterday = (datetime.now() - timedelta(days=1))
    date_str = yesterday.strftime("%d.%m.%Y")
    filename = f"நடப்பு_கால_நிகழ்வுகள்_{date_str}.txt"
    
    # Save content to a temporary file
    filepath = f"/tmp/{filename}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    sent = 0
    failed = 0
    failed_channels = []
    
    for i, channel in enumerate(ALL_CHANNELS):
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/sendDocument",
                    data={
                        "chat_id": channel,
                        "caption": f"📚 {title}\n\n🔗 கல்வி உபகரண விற்பனை நிலையம்\nhttps://employmenttamil.in/shop/"
                    },
                    files={"document": (filename, f, "text/plain")},
                    timeout=30
                )
            
            if resp.status_code == 200 and resp.json().get("ok"):
                sent += 1
            else:
                failed += 1
                failed_channels.append(str(channel))
        except Exception as e:
            failed += 1
            failed_channels.append(str(channel))
        
        # Rate limiting
        time.sleep(0.1)
        if (i + 1) % 20 == 0:
            time.sleep(1.5)
    
    return sent, failed, failed_channels


def run_daily_task():
    """Main task: collect news, generate content, send to channels"""
    print("Starting daily current affairs task...")
    
    result = generate_current_affairs()
    if not result:
        print("Failed to generate content")
        # Notify owner
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": OWNER_ID,
            "text": "❌ Current affairs generation failed today. Please check logs."
        })
        return
    
    title, content = result
    print(f"Content generated: {title}")
    
    # Send to all channels
    sent, failed, failed_channels = send_document_to_channels(title, content)
    
    # Notify owner
    status_msg = f"✅ Daily Current Affairs Sent!\n\n"
    status_msg += f"📄 {title}\n"
    status_msg += f"📤 Sent: {sent}/{len(ALL_CHANNELS)} channels\n"
    if failed > 0:
        status_msg += f"❌ Failed: {failed}\n"
        status_msg += f"Failed channels: {', '.join(failed_channels[:10])}"
    
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": OWNER_ID,
        "text": status_msg
    })
    
    print(f"Done! Sent to {sent} channels, {failed} failed")


# ============ SCHEDULER ============
def check_schedule():
    """Check if it's 7 AM IST and run the task"""
    import pytz
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.hour == 7 and now.minute < 5:
        run_daily_task()


def scheduler_loop():
    """Background scheduler that checks every minute"""
    import pytz
    last_run_date = None
    
    while True:
        try:
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            today = now.date()
            
            # Run at 7 AM IST, only once per day
            if now.hour == 7 and now.minute < 5 and last_run_date != today:
                last_run_date = today
                run_daily_task()
            
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(60)


# ============ FLASK ROUTES ============
@app.route("/", methods=["GET"])
def health():
    """Health check endpoint for UptimeRobot"""
    return jsonify({"status": "alive", "bot": "TNPSC Current Affairs"})


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Handle Telegram webhook updates"""
    update = request.get_json()
    
    if not update:
        return jsonify({"ok": True})
    
    message = update.get("message")
    if not message:
        return jsonify({"ok": True})
    
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    user_id = message.get("from", {}).get("id")
    
    # Only respond to owner
    if user_id != OWNER_ID:
        return jsonify({"ok": True})
    
    if text == "/generate":
        # Manual trigger to generate and send current affairs
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⏳ Generating current affairs... This may take 2-3 minutes."
        })
        # Run in background thread
        thread = threading.Thread(target=run_daily_task)
        thread.start()
    
    elif text == "/status":
        import pytz
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"✅ Bot is running\n🕐 Current IST: {now.strftime('%H:%M %d-%m-%Y')}\n📢 Channels: {len(ALL_CHANNELS)}\n⏰ Next run: 7:00 AM IST"
        })
    
    elif text == "/help":
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": "📚 TNPSC Current Affairs Bot\n\n/generate - Generate & send now\n/status - Check bot status\n/help - Show this message"
        })
    
    return jsonify({"ok": True})


# Start scheduler in background
scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
