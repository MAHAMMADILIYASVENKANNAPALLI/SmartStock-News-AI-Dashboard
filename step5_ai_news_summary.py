import requests
import google.generativeai as genai

# Gemini API key
API_KEY = "AIzaSyBH4COoxm0QRQpMC3il4GYEDna2kVbtzG0"  # Replace with your key
genai.configure(api_key=API_KEY)

# NewsAPI key
NEWS_API_KEY = "9089e4981e7e4cf084b9abaecf6b55d9"  # Replace with your key

url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        print("⚠️ No news articles found.")
    else:
        model = genai.GenerativeModel("gemini-flash-latest")

        for i, article in enumerate(articles[:3], start=1):
            title = article.get("title", "No title")
            description = article.get("description", "No description available.")
            content = f"Title: {title}\nDescription: {description}"

            print(f"\n📰 {i}. {title}")
            print(f"🔗 {article['url']}")

            try:
                prompt = f"Summarize this financial news in 2-3 lines:\n\n{content}"
                response = model.generate_content(prompt)
                print("🤖 AI Summary:", response.text.strip())
            except Exception as e:
                print("⚠️ Error generating AI summary:", e)
else:
    print("⚠️ Failed to fetch news. Status code:", response.status_code)
