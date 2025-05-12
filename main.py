import os
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from twocaptcha import TwoCaptcha
from db.mongo_handler import insert_articles
from bson import ObjectId  # 👈 Added for ObjectId conversion
import requests
from dotenv import load_dotenv
from db.mongo_handler import insert_summaries  # ✅ Mongo insert
import schedule
from email_module import build_html_email, send_newsletter
from pymongo import MongoClient

# from scraper_prime import scrapper
# from summerizer_prime import summery
# from filter_prime import filter
# from emailer_prime import emailer

def scrapper():
    
    API_KEY = 'YOUR_2CAPTCHA_API_KEY'  # Replace with your 2Captcha key
    
    # Create timestamped folder for output
    def create_output_folder():
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        folder_path = os.path.join('json', timestamp)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    # 🔁 Recursively convert ObjectIds to strings
    # 🔁 Recursively convert ObjectIds and datetime to strings
    def convert_objectid(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, list):
            return [convert_objectid(i) for i in obj]
        if isinstance(obj, dict):
            return {k: convert_objectid(v) for k, v in obj.items()}
        return obj
    
    
    # Save all results to one file
    def save_all_data_to_json(all_data, folder_path):
        file_path = os.path.join(folder_path, "scrap.json")
        cleaned_data = convert_objectid(all_data)  # 🧹 Clean ObjectIds
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Data saved to {file_path}")
    
    # Scrap 1
    def scrap_1():
        print("Running scrap_1...")
        data = []
    
        def solve_captcha(page):
            print("Solving CAPTCHA...")
            captcha_image = page.locator('img').screenshot(path='captcha_image.png')
            solver = TwoCaptcha(API_KEY)
            try:
                result = solver.normal('captcha_image.png')
                return result['code']
            except Exception as e:
                print(f"Captcha solve failed: {e}")
                return None
    
        def extract_full_article(page, url):
            page.goto(url)
            page.wait_for_timeout(3000)
            soup = BeautifulSoup(page.content(), "html.parser")
            # Try selecting the right class
            content_divs = soup.select("div.paragraph--type--content-block-text")
            if content_divs:
                all_paragraphs = []
                for div in content_divs:
                    paragraphs = div.find_all("p")
                    all_paragraphs.extend([p.get_text(strip=True) for p in paragraphs])
                return "\n".join(all_paragraphs)
            return "❌ Full article not found."
    
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://news.mit.edu/topic/artificial-intelligence2/")
            page.wait_for_timeout(5000)
    
            if page.query_selector('img[src*="captcha"]'):
                code = solve_captcha(page)
                if code:
                    page.fill('input[name="captcha"]', code)
                    page.click('button[type="submit"]')
                    page.wait_for_timeout(5000)
    
            soup = BeautifulSoup(page.content(), "html.parser")
            articles = soup.find_all("article", class_="term-page--news-article--item")
    
            for item in articles:
                title_tag = item.find("h3")
                link_tag = item.find("a", href=True)
                if not title_tag or not link_tag:
                    continue
                title = title_tag.get_text(strip=True)
                url = "https://news.mit.edu" + link_tag["href"]
                full_text = extract_full_article(page, url)
                data.append({
                    "title": title,
                    "url": url,
                    "content": full_text,
                    "source": "MIT News",
                    "type":"scrap"
                })
    
            browser.close()
    
        return data
    
    # Scrap 2
    def scrap_2():
        print("Running scrap_2...")
        data = []
    
        def extract_full_article(page, url):
            page.goto(url)
            page.wait_for_timeout(3000)
            soup = BeautifulSoup(page.content(), "html.parser")
            content_div = soup.select_one("div.entry-content")
            if content_div:
                paragraphs = content_div.find_all("p")
                return "\n".join(p.get_text(strip=True) for p in paragraphs)
            return "❌ Full article not found."
    
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://techfundingnews.com/category/AI/")
            page.wait_for_timeout(5000)
    
            soup = BeautifulSoup(page.content(), "html.parser")
            articles = soup.select("li.pk-post-item article")
    
            for item in articles:
                link_tag = item.select_one("h3.cs-entry__title a")
                if not link_tag:
                    continue
                title = link_tag.get_text(strip=True)
                url = link_tag["href"]
                full_text = extract_full_article(page, url)
                data.append({
                    "title": title,
                    "url": url,
                    "content": full_text,
                    "source": "Tech Funding News",
                    "type":"scrap"
    
                })
    
            browser.close()
    
        return data
    
    # Scrap 3
    def scrap_3():
        print("Running scrap_3...")
        data = []
    
        def extract_full_article(page, url):
            page.goto(url)
            page.wait_for_timeout(3000)
            soup = BeautifulSoup(page.content(), "html.parser")
            content_div = soup.select_one("div.entry-content")
            if content_div:
                paragraphs = content_div.find_all("p")
                return "\n".join(p.get_text(strip=True) for p in paragraphs)
            alt_content = soup.select_one("div.text-gray-700.whitespace-pre-wrap")
            if alt_content:
                return alt_content.get_text(strip=True, separator="\n")
            return "❌ Full article not found."
    
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
    
            url = "https://aiagentstore.ai/ai-agent-news/this-week/"
            page.goto(url)
            page.wait_for_timeout(5000)
    
            soup = BeautifulSoup(page.content(), "html.parser")
            content = soup.select_one("div.text-gray-700.whitespace-pre-wrap")
    
            if content:
                full_text = extract_full_article(page, url)
                data.append({
                    "title": "AI Agent Developments Summary",
                    "url": url,
                    "content": full_text,
                    "source": "AI Agent Store",
                    "type":"scrap"
    
                })
    
            browser.close()
    
        return data
    
    # Run all and save to single file
    def main():
        output_folder = create_output_folder()
        all_data = []
    
        # Scrap 1
        scrap1_data = scrap_1()
        all_data.extend(scrap1_data)
        insert_articles(scrap1_data)
        time.sleep(3)
    
        # Scrap 2
        scrap2_data = scrap_2()
        all_data.extend(scrap2_data)
        insert_articles(scrap2_data)
        time.sleep(3)
    
        # Scrap 3
        scrap3_data = scrap_3()
        all_data.extend(scrap3_data)
        insert_articles(scrap3_data)
    
        # Save combined data
        save_all_data_to_json(all_data, "./json/final/")
    main()

def summery():
     # Load .env file
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-8b-8192"
    
    # Set paths
    SCRAPE_FOLDER = "json/final"
    INPUT_PATH = os.path.join(SCRAPE_FOLDER, "scrap.json")
    OUTPUT_PATH = os.path.join(SCRAPE_FOLDER, "summery.json")
    
    # Load scraped data
    def load_scraped_data(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ✅ Summarize with enforced 2s delay and retry
    def summarize_with_groq(content, retries=5, delay=2, backoff=2):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
    
        prompt = (
            "Summarize the following article into one short paragraph and only give the article, "
            "no pretext or posttext like: 'Here is a summary of the article in one paragraph:' — "
            "nothing but directly the paragraph:\n\n" + content
        )
    
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
    
        for attempt in range(1, retries + 1):
            time.sleep(delay)  # ⏲️ Always wait before each request
    
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=body
                )
    
                if response.status_code == 429:
                    print(f"⚠️ Attempt {attempt}: Rate limited (429). Retrying in {delay}s...")
                    delay *= backoff
                    continue
                
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content'].strip()
    
            except requests.exceptions.RequestException as e:
                print(f"❌ Attempt {attempt}: Error - {e}")
                delay *= backoff
    
        return "Summary failed after retries."
    
    # Save summarized output
    def save_summaries(summaries, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=4)
        print(f"✅ Summarized data saved to {output_path}")
    
    # Main logic
    def main():
        if not os.path.exists(INPUT_PATH):
            print("❌ Input JSON file not found.")
            return
    
        articles = load_scraped_data(INPUT_PATH)
        summarized_articles = []
    
        for i, article in enumerate(articles):
            print(f"🔹 Summarizing article {i+1}/{len(articles)}: {article['title']}")
    
            content_to_summarize = article.get('content') or article['title']
    
            summary = summarize_with_groq(content_to_summarize)
            summarized_articles.append({
                "title": article['title'],
                "url": article.get('url', ''),
                "source": article['source'],
                "summary": summary,
                "type": "summary"
            })
    
        save_summaries(summarized_articles, OUTPUT_PATH)
        insert_summaries(summarized_articles)
    main()
def filterr():
     # Load .env file
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-8b-8192"

    # Set paths
    SCRAPE_FOLDER = "json/final"
    INPUT_PATH = os.path.join(SCRAPE_FOLDER, "summery.json")
    OUTPUT_PATH = os.path.join(SCRAPE_FOLDER, "filter.json")

    # Load summarized data
    def load_summarized_data(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Summarize with Groq
    def categorize_with_groq(content_batch):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # prompt = f"Categorize the following articles into 'Top AI News', 'AI Funding Updates', and 'New News About Agents'.\n\nArticles:\n{content_batch}"
        prompt = (
        "You will be given a batch of AI article summaries. Your task is to categorize each article "
        "into one of the following categories: \n"
        "1. Top AI News\n"
        "2. AI Funding Updates\n"
        "3. New News About Agents\n\n"
        "Return the category name for each article in the same order as given. "
        "If fewer than 6 articles are clearly categorizable (based on content), "
        "still distribute all of them into the three categories in a reasonable way to make up a total of 6 articles. "
        "and remember not more than 6 in total accross all the categories not at all more than 6 in total"

        "Format your response as a plain list — one category per line, matching the order of the input articles.\n\n"
        f"Articles:\n{content_batch}"
    )

        body = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Error categorizing: {e}")
            return None

    # Batch articles to avoid hitting token limits
    def batch_articles(articles, batch_size=5):
        for i in range(0, len(articles), batch_size):
            yield articles[i:i + batch_size]

    # Scrape additional articles for underpopulated categories
    def scrape_additional_articles(category):
        print(f"🔹 Scraping additional articles for {category}...")
        # Add specific scraping logic for missing categories.
        # Example:
        if category == "Top AI News":
            # Scrape articles for Top AI News
            pass
        elif category == "AI Funding Updates":
            # Scrape articles for AI Funding Updates
            pass
        elif category == "New News About Agents":
            # Scrape articles for New News About Agents
            pass
        return []

    # Main logic
    def main():
        if not os.path.exists(INPUT_PATH):
            print("❌ Input JSON file not found.")
            return

        # Load the summarized data
        summarized_articles = load_summarized_data(INPUT_PATH)
        filtered_articles = {
            "Top AI News": [],
            "AI Funding Updates": [],
            "New News About Agents": []
        }

        # Categorize the articles in batches to avoid token limits
        for batch in batch_articles(summarized_articles, batch_size=5):
            content_batch = "\n".join([f"Title: {article['title']}\nSummary: {article['summary']}" for article in batch])
            print(f"🔹 Categorizing batch of {len(batch)} articles...")

            categorized_response = categorize_with_groq(content_batch)

            if categorized_response:
                # Example response format from Groq
                categories = categorized_response.split("\n")

                # Assign articles to categories based on Groq's response
                for i, article in enumerate(batch):
                    if "Top AI News" in categories[i]:
                        filtered_articles["Top AI News"].append(article)
                    elif "AI Funding Updates" in categories[i]:
                        filtered_articles["AI Funding Updates"].append(article)
                    elif "New News About Agents" in categories[i]:
                        filtered_articles["New News About Agents"].append(article)

            time.sleep(1)  # Avoid rate limits

        # Check if any category is empty and scrape additional articles if needed
        for category in filtered_articles:
            if len(filtered_articles[category]) == 0:
                print(f"⚠️ No articles for category: {category}")
                additional_articles = scrape_additional_articles(category)
                filtered_articles[category].extend(additional_articles)

        # Insert filtered articles into MongoDB using insert_summaries
        all_filtered_summaries = []
        for category, articles in filtered_articles.items():
            for article in articles:
                all_filtered_summaries.append({
                    "title": article["title"],
                    "url": article.get("url", ""),
                    "source": article.get("source", ""),
                    "summary": article["summary"],
                    "category": category,
                    "type":"filter"
                })

        # Insert filtered summaries into the MongoDB collection
        insert_summaries(all_filtered_summaries)

        # Save the filtered articles to a new JSON file
        save_filtered_articles(filtered_articles, OUTPUT_PATH)

    # Save filtered articles
    def save_filtered_articles(filtered_articles, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_articles, f, ensure_ascii=False, indent=4)
        print(f"✅ Filtered articles saved to {output_path}")
    main()


def emailer():
    # MongoDB connection URI and database/collection names
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "buyerPassdn"
    COLLECTION_NAME = "mail_subscribers"

    FILTERED_DATA_PATH = "./json/final/filter.json"

    def load_filtered_data():
        try:
            with open(FILTERED_DATA_PATH, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"❌ File not found: {FILTERED_DATA_PATH}")
        except json.JSONDecodeError:
            print(f"❌ Error decoding JSON from {FILTERED_DATA_PATH}")
        return {}

    def fetch_recipients():
        """Fetch recipient name and email from MongoDB."""
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Fetch all users with valid emails
        users = collection.find({"email": {"$exists": True}})
        recipients = [{"name": user["name"], "email": user["email"]} for user in users]

        client.close()
        return recipients

    def send_daily_newsletter():
        print("📧 Preparing to send daily AI newsletter...")

        filtered_articles = load_filtered_data()
        if not filtered_articles:
            print("❌ No filtered articles found. Email not sent.")
            return

        html_content = build_html_email(filtered_articles)
        recipients = fetch_recipients()

        if not recipients:
            print("❌ No recipients found in the database.")
            return

        for recipient in recipients:
            send_newsletter([recipient["email"]], html_content)
            print(f"✅ Newsletter sent to {recipient['name']} ({recipient['email']})")

    # def start_scheduler():
    #     schedule.every().day.at("18:31").do(send_daily_newsletter)
    #     print("⏰ Email scheduler is running. Waiting for 16:05 daily...")
    
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(60)
    send_daily_newsletter()

def run_pipeline():
    scrapper()
    time.sleep(15)
    summery()
    time.sleep(15)

    filterr()
    time.sleep(15)

    emailer()

# Schedule the full pipeline to run at 9:00 AM daily
schedule.every().day.at("16:19").do(run_pipeline)

print("📅 Scheduler started. Waiting for 9:00 AM daily to run the pipeline...")

while True:
    schedule.run_pending()
    time.sleep(1)