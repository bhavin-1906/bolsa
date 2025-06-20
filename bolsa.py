import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import types
try:
    import feedparser
except ModuleNotFoundError:  # simple fallback when feedparser is missing
    feedparser = types.ModuleType("feedparser")
    def _parse(*_args, **_kwargs):
        return types.SimpleNamespace(entries=[])
    feedparser.parse = _parse
    sys.modules['feedparser'] = feedparser
try:
    import yfinance as yf
except ModuleNotFoundError:  # fallback when yfinance isn't installed
    yf = types.ModuleType("yfinance")
    class _DummyTicker:
        def __init__(self, *_a, **_kw):
            self.info = {}
        def history(self, *args, **kwargs):
            return types.SimpleNamespace(tail=lambda n: types.SimpleNamespace(to_dict=lambda: {}))
    yf.Ticker = _DummyTicker
    sys.modules['yfinance'] = yf
try:
    import schedule
except ModuleNotFoundError:
    class _DummySchedule:
        def every(self):
            return self

        def day(self):
            return self

        def at(self, *_args, **_kwargs):
            return self

        def do(self, *_args, **_kwargs):
            return self

        def run_pending(self):
            pass

    schedule = _DummySchedule()
import time

# Placeholder summarization using simple truncation

def summarize(text: str, max_chars: int = 200) -> str:
    return text[:max_chars] + '...'


def fetch_feed(url: str) -> List[Dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'summary': summarize(entry.get('summary', '')),
        })
    return articles


def gather_news() -> List[Dict]:
    feeds = {
        'Financial Times': 'https://www.ft.com/?format=rss',
        'Economist': 'https://www.economist.com/latest/rss.xml',
        'Wall Street Journal': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    }
    news = []
    for source, url in feeds.items():
        try:
            articles = fetch_feed(url)
            for article in articles:
                article['source'] = source
                news.append(article)
        except Exception as exc:
            print(f"Failed to fetch from {source}: {exc}")
    return news


def analyze_stock(ticker: str) -> Dict:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        current_price = stock.info.get('regularMarketPrice')
        pe_ratio = stock.info.get('trailingPE')
        return {
            'ticker': ticker,
            'current_price': current_price,
            'pe_ratio': pe_ratio,
            'history': hist.tail(5).to_dict(),
        }
    except Exception as exc:
        print(f"Failed to fetch stock data for {ticker}: {exc}")
        return {}


def select_stocks(tickers: List[str]) -> List[Dict]:
    recommendations = []
    seen = set()
    for ticker in tickers:
        data = analyze_stock(ticker)
        if data:
            symbol = data.get('ticker')
            if (
                symbol
                and symbol not in seen
                and data.get('pe_ratio')
                and data['pe_ratio'] < 25
            ):
                seen.add(symbol)
                recommendations.append(data)
        if len(recommendations) >= 5:
            break
    return recommendations


def compose_report(news: List[Dict], stocks: List[Dict]) -> str:
    lines = []
    lines.append("Today's Financial News:\n")
    for item in news:
        lines.append(f"- {item['source']}: {item['title']} ({item['link']})")
    lines.append("\nStock Recommendations:\n")
    for stock in stocks:
        lines.append(f"- {stock['ticker']} at {stock['current_price']} (PE {stock['pe_ratio']})")
    return '\n'.join(lines)


def send_email(report: str, recipient: str):
    msg = MIMEMultipart()
    msg['Subject'] = 'Daily Financial Briefing'
    msg['From'] = os.environ.get('EMAIL_FROM', 'noreply@example.com')
    msg['To'] = recipient
    msg.attach(MIMEText(report, 'plain'))

    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    if not smtp_server or not smtp_user or not smtp_pass:
        print('SMTP credentials not configured.')
        return
    try:
        with smtplib.SMTP_SSL(smtp_server) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as exc:
        print(f"Failed to send email: {exc}")


def job(recipient: str):
    news = gather_news()
    # Placeholder tickers from news articles - this could be extracted with NLP
    example_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    stocks = select_stocks(example_tickers)
    report = compose_report(news, stocks)
    send_email(report, recipient)


def schedule_daily(recipient: str, hour: int = 8, minute: int = 0):
    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job, recipient=recipient)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    target_email = os.environ.get('TARGET_EMAIL', 'user@example.com')
    # For manual run without scheduling
    job(target_email)
    # To enable scheduling, uncomment the next line
    # schedule_daily(target_email)
