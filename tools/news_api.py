import feedparser

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=(Tokyo+AND+(weather+OR+storm+OR+typhoon+OR+rain+OR+flood+OR+heatwave))"
    "&hl=en-IN&gl=IN&ceid=IN:en"
)

feed = feedparser.parse(RSS_URL)

for entry in feed.entries[:10]:
    print("TITLE:", entry.title)
    print("SOURCE:", entry.get("source", {}).get("title", "Unknown"))
    print("PUBLISHED:", entry.get("published", "N/A"))

    # Summary
    summary = entry.get("summary", "").replace("<b>", "").replace("</b>", "")
    print("SUMMARY:", summary)

    # ← This is the URL the user taps for more details
    print("LEARN MORE:", entry.link)

    print("-" * 80)
