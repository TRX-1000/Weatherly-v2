import feedparser
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import re


class NewsWorker(QThread):
    """Background thread for fetching news"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, city):
        super().__init__()
        self.city = city
    
    def strip_html(self, text):
        """Remove all HTML tags from text"""
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean
    
    def run(self):
        try:
            # Properly encode the city name for URL
            city_encoded = quote_plus(self.city)
            
            # Try multiple RSS feeds to get the most recent news
            rss_urls = [
                # Recent news with "when:7d" parameter for last 7 days
                f"https://news.google.com/rss/search?q={city_encoded}+weather+when:7d&hl=en-US&gl=US&ceid=US:en",
                # Broader search with location
                f"https://news.google.com/rss/search?q={city_encoded}+(weather+OR+forecast+OR+temperature)&hl=en-US&gl=US&ceid=US:en",
                # Alternative with "after:" parameter
                f"https://news.google.com/rss/search?q={city_encoded}+weather&hl=en-US&gl=US&ceid=US:en",
            ]
            
            all_entries = []
            
            # Try each RSS feed
            for rss_url in rss_urls:
                feed = feedparser.parse(rss_url)
                if feed.entries:
                    all_entries.extend(feed.entries)
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_entries = []
            for entry in all_entries:
                if entry.title not in seen_titles:
                    seen_titles.add(entry.title)
                    unique_entries.append(entry)
            
            # Parse and filter entries
            news_items = []
            current_date = datetime.now()
            thirty_days_ago = current_date - timedelta(days=30)
            
            for entry in unique_entries[:20]:  # Check more entries
                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6])
                    except:
                        pass
                
                # Skip if older than 30 days
                if published_date and published_date < thirty_days_ago:
                    continue
                
                # Clean all text fields of HTML
                title = self.strip_html(entry.title)
                source = entry.get("source", {}).get("title", "Unknown")
                published = entry.get("published", "N/A")
                summary = self.strip_html(entry.get("summary", ""))
                link = entry.link
                
                news_items.append({
                    "title": title,
                    "source": source,
                    "published": published,
                    "summary": summary,
                    "link": link,
                    "date": published_date
                })
                
                # Stop once we have 5 recent items
                if len(news_items) >= 5:
                    break
            
            # Sort by date (most recent first)
            news_items.sort(key=lambda x: x.get("date") or datetime.min, reverse=True)
            
            # Remove the date field before sending (not needed in UI)
            for item in news_items:
                item.pop("date", None)
            
            self.finished.emit(news_items)
        except Exception as e:
            self.error.emit(str(e))


class NewsAPI:
    def __init__(self):
        pass
    
    def get_weather_news(self, city, callback, error_callback):
        """Fetch weather-related news for a city"""
        worker = NewsWorker(city)
        worker.finished.connect(callback)
        worker.error.connect(error_callback)
        worker.start()
        return worker  # Return to keep reference