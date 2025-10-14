import requests
import google.generativeai as genai
import json
from datetime import datetime

# Your API keys
GEMINI_API_KEY = "your own GEMINI API KEY"
NEWS_API_KEY = "YOUR OWN NEWS API KEY"

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-flash-latest"
SUMMARY_FILE = "latest_news.json"

def fetch_and_summarize():
    NEWS_URL = f".....................................................................={NEWS_API_KEY}"
    response = requests.get(NEWS_URL)
    response.raise_for_status()
    articles = response.json().get("articles", [])[:6]
    summaries = []

    model = genai.GenerativeModel(MODEL_NAME)

    for article in articles:
        title = article.get("title", "No title")
        desc = article.get("description", "")
        content = f"Title: {title}\nDescription: {desc}"
        try:
            summary = model.generate_content(f"Summarize this business news in 2 short lines:\n\n{content}").text.strip()
        except Exception as e:
            summary = f"Error: {e}"

        summaries.append({"title": title, "url": article.get("url", ""), "summary": summary})

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(summaries)} news summaries saved to {SUMMARY_FILE} at {datetime.now()}")

if __name__ == "__main__":
    fetch_and_summarize()


