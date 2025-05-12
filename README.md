# 🚀 BuildingStartup - AI Daily Automation System

Automate your daily startup-building news flow with AI. BuildingStartup is a complete Python automation system that scrapes the latest AI/startup news, summarizes it using LLaMA-3 via Groq API, and emails a beautifully formatted newsletter to your subscribers.

<div align="center">
  
  
  ![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)
  ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green)
  ![LLM](https://img.shields.io/badge/LLM-LLaMA--3-orange)
  ![License](https://img.shields.io/badge/License-MIT-blue)
  
</div>

## 🧠 What is BuildingStartup?

BuildingStartup is your personal backend engine that runs every morning to help startup enthusiasts and founders stay ahead. It automates the boring parts:

- 🌐 **Scrapes** trending AI & startup news from trusted sources
- 📝 **Summarizes** articles into digestible insights using LLMs
- ✉️ **Sends** a daily curated email to all subscribers
- 🛠️ **Powered** by Python, MongoDB, Groq, and SMTP

## 🔁 System Architecture

```
+----------------+
| MongoDB Atlas  |<---- stores subscriber emails
+----------------+
        |
        ↓
+----------------+     +----------------+
| Scraper (Selenium) → |  Raw AI News   |
+----------------+     +----------------+
        ↓
+---------------------+
| Groq API (LLaMA3)   | ← Summarization
+---------------------+
        ↓
+--------------------------+
| JSON + Filter Module     |
+--------------------------+
        ↓
+-------------------------------+
| HTML Generator (Jinja2 Email) |
+-------------------------------+
        ↓
+-----------------------+
| Gmail SMTP Mailer     |
+-----------------------+
```

## 🗂️ Project Structure

```
backend/
├── db/                          # MongoDB models and connection setup
├── emailer/
│   └── email_service.py         # Email formatting & sending logic
├── json/                        # Temporary storage for scraped/summarized data
├── scheduler/
│   └── daily_job.py             # Scheduled execution logic
├── scraper/
│   └── scraper_prime.py         # News scraper for AI/startup sites
├── subscribers/
│   └── email_list.json          # [Deprecated] Use MongoDB now
├── summarizer/
│   └── summerizer_prime.py      # Groq API summarizer
├── templates/
│   └── newsletter_template.html # Jinja2 HTML template
├── __pycache__/
├── .env                         # API keys and secrets
├── .gitignore
├── daily_runner.py              # Single-entry script for full pipeline
├── email_module.py              # SMTP + Jinja2 template engine
├── filter_prime.py              # Content filter logic
├── emailer_prime.py             # MongoDB-based mailing logic
├── main.py                      # Dev/test orchestration script
├── test_send_newsletter.py      # Manual test script
├── README.md                    # ✅ You're reading it
├── requirements.txt             # ✅ All needed packages
```

## ✅ Features

- ✅ **Fully automated** daily job at 9:00 AM(change the time according to you in the main.py)
- ✅ **10-second delays** between each major task (to throttle APIs)
- ✅ **Groq API integration** using LLaMA3
- ✅ **MongoDB support** for dynamic subscriber list
- ✅ **Clean HTML formatting** via Jinja2
- ✅ **Secure Gmail SMTP** (via App Passwords)
- ✅ **Modular code** for easy testing and development

## ⚙️ How to Set Up (Local Dev)

### 1. Clone the repo
```bash
git clone https://github.com/devang99999/mailer.git
"and just run python main.py command after changing the daily running time in the main.py"
```

### 2. Install requirements
```bash
pip install -r requirements.txt
```

### 3. Create .env file
```env
GMAIL_USER=your@gmail.com
GMAIL_PASS=your-app-password
GROQ_API_KEY=your-groq-api-key
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/your-db
```

### 4. Add your MongoDB collection
Ensure your subscribers collection looks like:

```json
{
  "_id": "681f490363853972532c758f",
  "name": "Test User",
  "email": "test@test.com",
  "createdAt": "2025-05-10T12:39:31.535Z"
}
```

### 5. Run manually to test everything:
```bash
python main.py
```

## 🕒 Running Daily (Prod Mode)

Run the full automation with:

```bash
python main.py
```

This runs every day at 9:00 AM, and in this order:

1. Scraper
2. Summarizer
3. Filter
4. Mailer

(With 10-second delays in between)

You'll see logs like:

```
🔍 Scraping articles...
📝 Summarizing via Groq...
🔎 Filtering summaries...
📧 Sending daily email...
✅ Done.
```

## 📦 requirements.txt

```
beautifulsoup4==4.12.2
requests==2.31.0
selenium==4.20.0
schedule==1.2.1
python-dotenv==1.0.1
openai==1.23.2
jinja2==3.1.3
pymongo==4.6.3
```

## 🧪 Development + Testing Tips

- Use `main.py` to test end-to-end logic in dev mode
- `filter_prime.py` can be used to customize topic filtering rules
- Use `email_module.py` to preview emails before going live
- `emailer_prime.py` handles MongoDB-based dynamic emailing

## 📈 Future Improvements

- [ ] Web dashboard to view subscriber metrics
- [ ] Automatic bounce handling for emails
- [ ] RSS-based multi-source scraping
- [ ] GPT-4 summarization fallback
- [ ] Open-tracking in emails

## 🧠 Who Is This For?

- Indie Hackers building products every morning
- Startup teams that want an automated daily AI feed
- Researchers looking for clean, summarized tech insights



For issues, ideas, or contributions, contact <a href="https://github.com/devang99999">Devang</a>.

> **Note:** Test the system for 2-3 days before full production.<br/>
> **Note:** consider sending the news letter weekly as the websites are not updated daily.
