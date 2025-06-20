# Bolsa

A simple Python script that aggregates daily financial news from major sources and emails a short briefing with stock recommendations.

## Features

- Fetches RSS feeds from the Financial Times, The Economist, and The Wall Street Journal.
- Summarizes articles (placeholder summarization).
- Pulls stock data using `yfinance` and selects up to five stocks with a low P/E ratio as an example strategy.
- Sends the compiled report via email.
- Can be scheduled to run every morning at 8 AM.

## Usage

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables for email sending:

- `SMTP_SERVER` – SMTP server address (required)
- `SMTP_PORT` – SMTP port (defaults to `465` for SSL)
- `SMTP_USER` or `SMTP_USERNAME` – SMTP username (optional)
- `SMTP_PASS` or `SMTP_PASSWORD` – SMTP password (optional)
- `EMAIL_FROM` – From address for the email
- `TARGET_EMAIL` – Recipient address

3. Run the script manually:

```bash
python bolsa.py
```

To enable daily scheduling at 8 AM, uncomment the `schedule_daily` call at the bottom of `bolsa.py` and run the script on a server or machine that stays on.

## Limitations

This repository contains example code only. Running it requires internet connectivity for fetching news and stock data as well as sending emails. The summarization logic is a simple placeholder.
