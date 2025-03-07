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

async def send_message_telegram(message, link=None):
    """
    Send a message to a Telegram channel with an optional link button.
    
    Args:
        message: The message text to send
        link: URL to include as a button (optional)
        
    Returns:
        dict: The JSON response from the Telegram API call
        
    Raises:
        TelegramAPIError: If the API call fails
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        raise TelegramAPIError("Telegram Bot Token not configured. Please set the TELEGRAM_BOT_TOKEN environment variable.")
        
    if not TELEGRAM_CHANNEL_ID:
        logger.error("TELEGRAM_CHANNEL_ID environment variable is not set")
        raise TelegramAPIError("Telegram Channel ID not configured. Please set the TELEGRAM_CHANNEL_ID environment variable.")
    
    # Telegram message character limit
    MAX_MESSAGE_LENGTH = 4096
    
    # Helper function to make API calls to Telegram
    def call_telegram_api(text, include_button=False):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "html"
        }
        
        if include_button and link:
            keyboard = {
                "inline_keyboard": [[{"text": "View on Perplexity", "url": link}]]
            }
            data["reply_markup"] = json.dumps(keyboard)
        
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
    
    # If message is within limits, send as a single message
    if len(message) <= MAX_MESSAGE_LENGTH:
        return call_telegram_api(message, include_button=(link is not None))
    
    # If message exceeds limit, split and send as multiple messages
    else:
        logger.warning(f"Message exceeds Telegram's character limit ({len(message)} > {MAX_MESSAGE_LENGTH}). Splitting into multiple messages.")
        
        # Split the message into chunks of MAX_MESSAGE_LENGTH
        chunks = []
        for i in range(0, len(message), MAX_MESSAGE_LENGTH):
            chunks.append(message[i:i + MAX_MESSAGE_LENGTH])
        
        # Send all chunks except the last one without a button
        for i in range(len(chunks) - 1):
            chunk_message = f"Part {i+1}/{len(chunks)}\n\n{chunks[i]}"
            call_telegram_api(chunk_message, include_button=False)
        
        # Send the last chunk with the button if provided
        last_chunk = f"Part {len(chunks)}/{len(chunks)}\n\n{chunks[-1]}"
        return call_telegram_api(last_chunk, include_button=(link is not None))





