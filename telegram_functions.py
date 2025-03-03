from dotenv import load_dotenv
import os
import logging
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

class TelegramAPIError(Exception):
    """Custom exception for Telegram API errors"""
    pass

async def send_message_telegram(message, link):
    """
    Send a message to a Telegram channel with a link button.
    
    Args:
        message: The message text to send
        link: URL to include as a button
        
    Returns:
        dict: The JSON response from Telegram API
        
    Raises:
        TelegramAPIError: If the API call fails
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        raise TelegramAPIError("Telegram Bot Token not configured. Please set the TELEGRAM_BOT_TOKEN environment variable.")
        
    if not TELEGRAM_CHANNEL_ID:
        logger.error("TELEGRAM_CHANNEL_ID environment variable is not set")
        raise TelegramAPIError("Telegram Channel ID not configured. Please set the TELEGRAM_CHANNEL_ID environment variable.")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # send link as button
    keyboard = {
        "inline_keyboard": [[{"text": "View on Perplexity", "url": link}]]
    }
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "markdown",
        "reply_markup": keyboard
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        json_response = response.json()
        
        # Validate response structure
        if not json_response.get('ok'):
            error_description = json_response.get('description', 'Unknown error')
            logger.error(f"Telegram API error: {error_description}")
            raise TelegramAPIError(f"Telegram API error: {error_description}")
            
        return json_response
        
    except Timeout:
        logger.error("Request to Telegram API timed out")
        raise TelegramAPIError("Request to Telegram API timed out")
    except HTTPError as e:
        logger.error(f"HTTP error from Telegram API: {e.response.status_code} - {e.response.text}")
        raise TelegramAPIError(f"HTTP error from Telegram API: {e.response.status_code}")
    except RequestException as e:
        logger.error(f"Error making request to Telegram API: {str(e)}")
        raise TelegramAPIError(f"Error making request to Telegram API: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON response from Telegram API")
        raise TelegramAPIError("Invalid JSON response from Telegram API")
    except Exception as e:
        logger.error(f"Unexpected error when calling Telegram API: {str(e)}")
        raise TelegramAPIError(f"Unexpected error when calling Telegram API: {str(e)}")

def remove_spaces(text):
    return text.replace(" ", "")

def format_news_content_telegram(topic, news_content):
    """
    Format news content for Telegram message.
    
    Args:
        topic: The topic of the news
        news_content: List of news items with title and description
        
    Returns:
        str: Formatted message for Telegram
    """
    formatted_content = ""
    formatted_content += f"<b>#{remove_spaces(topic)}</b>\n\n"
    for news in news_content:
        formatted_content += f"<blockquote>{news['title']}</blockquote>\n{news['description']}\n\n\n"
    return formatted_content

