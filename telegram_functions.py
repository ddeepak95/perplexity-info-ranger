from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


import requests

async def send_message_telegram(message, link):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # send link as button
    keyboard = {
        "inline_keyboard": [[{"text": "View on Perplexity", "url": link}]]
    }
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

def remove_spaces(text):
    return text.replace(" ", "")

def format_news_content_telegram(topic, news_content):
    formatted_content = ""
    formatted_content += f"<b>#{remove_spaces(topic)}</b>\n\n"
    for news in news_content:
        formatted_content += f"<blockquote>{news['title']}</blockquote>\n{news['description']}\n\n\n"
    return formatted_content

