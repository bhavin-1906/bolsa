import os, sys; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import builtins
import types
from unittest import mock
from email.message import EmailMessage
import bolsa


def test_summarize():
    text = "a" * 50
    assert bolsa.summarize(text, max_chars=10) == "a" * 10 + "..."


def test_gather_news():
    fake_feed = types.SimpleNamespace(entries=[
        {
            "title": "Title1",
            "link": "http://example.com/1",
            "summary": "Summary1",
        }
    ])

    with mock.patch("feedparser.parse", return_value=fake_feed):
        news = bolsa.gather_news()
    assert len(news) == 3  # 3 sources, each yields one article
    sources = {n["source"] for n in news}
    assert sources == {"Financial Times", "Economist", "Wall Street Journal"}


def test_analyze_stock():
    class FakeTicker:
        def __init__(self, *args, **kwargs):
            self.info = {"regularMarketPrice": 100, "trailingPE": 20}

        def history(self, period="1y"):
            return types.SimpleNamespace(tail=lambda n: types.SimpleNamespace(to_dict=lambda: {"price": 100}))

    with mock.patch("yfinance.Ticker", return_value=FakeTicker()):
        data = bolsa.analyze_stock("FAKE")
    assert data["ticker"] == "FAKE"
    assert data["current_price"] == 100
    assert data["pe_ratio"] == 20


def test_select_stocks():
    with mock.patch("bolsa.analyze_stock", return_value={"ticker": "FAKE", "pe_ratio": 10, "current_price": 50}):
        recs = bolsa.select_stocks(["FAKE1", "FAKE2"])
    assert len(recs) == 1
    assert recs[0]["ticker"] == "FAKE"


def test_compose_report():
    news = [{"source": "FT", "title": "News", "link": "http://n"}]
    stocks = [{"ticker": "FAKE", "current_price": 50, "pe_ratio": 10}]
    report = bolsa.compose_report(news, stocks)
    assert "Today's Financial News" in report
    assert "FAKE" in report


def test_send_email(monkeypatch):
    class DummySMTP:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def login(self, user, password):
            self.user = user
            self.password = password

        def send_message(self, msg: EmailMessage):
            self.sent = msg

    dummy = DummySMTP()
    monkeypatch.setattr("smtplib.SMTP_SSL", lambda *a, **kw: dummy)
    monkeypatch.setenv("SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("SMTP_USER", "user")
    monkeypatch.setenv("SMTP_PASS", "pass")
    bolsa.send_email("report", "to@example.com")
    assert hasattr(dummy, "sent")

