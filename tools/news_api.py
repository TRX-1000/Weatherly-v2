import feedparser
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import re


class NewsWorker(QThread):
    """Background thread for fetching news"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def is_weather_article(self, title, summary):
        """Return True only if the article is genuinely weather-related."""

        text = f"{title} {summary}".lower()

        # Strong weather keywords (must contain at least one)
        must_have = [
            "weather", "forecast", "temperature", "rainfall",
            "storm", "cyclone", "hurricane", "tornado",
            "heatwave", "cold wave", "imd", "met office",
            "snowfall", "thunderstorm", "rain alert"
        ]

        if not any(word in text for word in must_have):
            return False

        # Blocklist for irrelevant content
        blocklist = [
            "book", "novel", "review", "movie", "show",
            "series", "trailer", "podcast", "author",
            "set in", "mystery", "crime", "celebrity",
            "music", "sports", "match", "fashion"
        ]

        if any(word in text for word in blocklist):
            return False

        return True
    
    def time_ago(self, dt):
        """Convert datetime to 'time-ago' text."""
        if not dt:
            return "Unknown"

        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()
        days = diff.days

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            return dt.strftime("%b %d, %Y")


    
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
                summary = self.strip_html(entry.get("summary", ""))
                link = entry.link

                # Check if genuinely weather-related
                if not self.is_weather_article(title, summary):
                    continue
                
                news_items.append({
                    "title": title,
                    "source": source,
                    "published": published_date.strftime("%b %d, %Y") if published_date else "Unknown",
                    "published_relative": self.time_ago(published_date),
                    "summary": summary,
                    "link": link,
                    "date": published_date
                })

                
                # Stop once we have 5 recent items
                if len(news_items) >= 10:
                    break
            
            # Sort by date (most recent first)
            news_items.sort(key=lambda x: x.get("date") or datetime.min, reverse=True)
            
            
            
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