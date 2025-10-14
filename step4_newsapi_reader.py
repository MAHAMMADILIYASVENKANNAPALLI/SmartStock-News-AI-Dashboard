import requests

API_KEY = "  Replace with your key "

url = f".........................................................={API_KEY}"
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

