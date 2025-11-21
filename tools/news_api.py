import requests 

API_KEY = "e35e9d9cc33d4125b220485f437b8679"
city = "London"

url = "http://newsapi.org/v2/everything"
params = {
    "q": f"weather {city}",
    "pageSize": 5,
    "sortBy": "publishedAt",
    "language": "en",
    "apiKey": API_KEY
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.text)

data = response.json()

for article in data.get("articles", []):
    print(f"{article['title']} ({article['source']['name']})")
    print(article['description'])
    print(article['url'])
    print()