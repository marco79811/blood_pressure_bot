import os
from datetime import datetime
from io import BytesIO

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import matplotlib.pyplot as plt

from db import db_session, init_db, Record

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

scheduler = BackgroundScheduler()


def send_daily_reminder():
    """Send a daily reminder message."""
    user_id = os.getenv("LINE_USER_ID")
    if user_id:
        line_bot_api.push_message(user_id, TextSendMessage(text="記得回報今天的血壓喔！"))


scheduler.add_job(send_daily_reminder, 'cron', hour=9, minute=0)
scheduler.start()


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if '/' in text:
        try:
            systolic, diastolic = map(int, text.split('/'))
            record = Record(
                timestamp=datetime.now(),
                systolic=systolic,
                diastolic=diastolic,
            )
            db_session.add(record)
            db_session.commit()
            reply = f"已記錄血壓：{systolic}/{diastolic}"
        except ValueError:
            reply = "請輸入正確的血壓格式，例如 120/80"
    else:
        reply = "請輸入血壓數值，例如 120/80"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))


@app.route('/export', methods=['GET'])
def export_csv():
    """Export records as CSV."""
    output = "timestamp,systolic,diastolic\n"
    for rec in db_session.query(Record).order_by(Record.timestamp):
        output += f"{rec.timestamp},{rec.systolic},{rec.diastolic}\n"
    return app.response_class(output, mimetype='text/csv')


@app.route('/trend', methods=['GET'])
def trend_image():
    """Return blood pressure trend image."""
    records = db_session.query(Record).order_by(Record.timestamp).all()
    if not records:
        return 'No data', 404
    dates = [rec.timestamp for rec in records]
    sys_vals = [rec.systolic for rec in records]
    dia_vals = [rec.diastolic for rec in records]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, sys_vals, label='Systolic')
    plt.plot(dates, dia_vals, label='Diastolic')
    plt.xlabel('Date')
    plt.ylabel('Pressure')
    plt.legend()
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
