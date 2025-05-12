import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["mailer"]  # You can change the database name
collection = db["mailer"]   # You can change the collection name
summary_collection = db["mailer"]  # Separate collection for summaries

# Insert articles into the database
def insert_articles(articles):
    def add_timestamp(doc):
        doc["timestamp"] = datetime.utcnow()
        return doc

    if isinstance(articles, list):
        if articles:
            articles_with_ts = [add_timestamp(article) for article in articles]
            collection.insert_many(articles_with_ts)
            print(f"✅ Inserted {len(articles)} articles into MongoDB.")
        else:
            print("⚠️ No articles to insert.")
    elif isinstance(articles, dict):
        article_with_ts = add_timestamp(articles)
        collection.insert_one(article_with_ts)
        print("✅ Inserted 1 article into MongoDB.")
    else:
        print("❌ Unsupported data format.")





# Insert summaries into the database
def insert_summaries(summaries):
    def add_timestamp(doc):
        doc["timestamp"] = datetime.utcnow()
        return doc

    if isinstance(summaries, list):
        if summaries:
            # Check for duplicates based on URL
            for summary in summaries:
                # if not summary_collection.find_one({"url": summary["url"]}):
                    summary_with_ts = add_timestamp(summary)
                    summary_collection.insert_one(summary_with_ts)
                    print(f"📝 Inserted summary for {summary['title']} into MongoDB.")
                # else:
                    # print(f"⚠️ Summary for {summary['title']} already exists in MongoDB.")
        else:
            print("⚠️ No summaries to insert.")
    elif isinstance(summaries, dict):
        if not summary_collection.find_one({"url": summaries["url"]}):
            summary_with_ts = add_timestamp(summaries)
            summary_collection.insert_one(summary_with_ts)
            print(f"📝 Inserted 1 summary into MongoDB.")
        else:
            print("⚠️ Summary already exists in MongoDB.")
    else:
        print("❌ Unsupported summary format.")

# Fetch the latest articles
def fetch_latest_articles(limit=10):
    return list(collection.find().sort("timestamp", -1).limit(limit))

# Fetch the latest summaries
def fetch_latest_summaries(limit=10):
    return list(summary_collection.find().sort("timestamp", -1).limit(limit))

# Clear all articles from the collection (Uncomment to use)
# def clear_articles():
#     collection.delete_many({})
#     print("🧹 Cleared all documents in the articles collection.")

# Clear all summaries from the collection (Uncomment to use)
# def clear_summaries():
#     summary_collection.delete_many({})
#     print("🧹 Cleared all documents in the summaries collection.")
