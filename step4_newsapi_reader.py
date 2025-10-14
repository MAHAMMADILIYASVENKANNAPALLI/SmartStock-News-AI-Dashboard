import requests

API_KEY = "9089e4981e7e4cf084b9abaecf6b55d9"  # Replace with your key

url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    articles = data.get("articles", [])

    if articles:
        for i, article in enumerate(articles[:5], start=1):
            print(f"📰 {i}. {article['title']}")
            print(f"🔗 {article['url']}")
            print(f"🧾 {article['description']}\n")
    else:
        print("No articles found.")
else:
    print("⚠️ Error:", response.status_code)
