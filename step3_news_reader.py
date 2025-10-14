import requests
from bs4 import BeautifulSoup

url = "............................"
headers = {......................}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1").text
    print("📰 Title:", title)
else:
    print("⚠️ Failed to fetch article, status code:", response.status_code)

