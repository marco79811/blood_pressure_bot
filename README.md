# Blood Pressure Line Bot

A simple Line Bot built with Flask to record blood pressure, send daily reminders and export trend charts.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set the following environment variables:

- `LINE_CHANNEL_SECRET` – your channel secret.
- `LINE_CHANNEL_ACCESS_TOKEN` – your channel access token.
- `LINE_USER_ID` – user ID to push daily reminder messages.

3. Run the application:

```bash
python app.py
```

The bot listens on port `5000`.

## Features

- Send a message like `120/80` to record a blood pressure reading.
- Daily reminder at 09:00 to input your reading.
- Access `/export` to download data as CSV.
- Access `/trend` to view a trend chart of your readings.
