import requests
from dotenv import load_dotenv
import os
import logging
import json
from requests.exceptions import RequestException, Timeout, HTTPError

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

PPLX_API_KEY = os.getenv("PPLX_API_KEY")

class PerplexityAPIError(Exception):
    """Custom exception for Perplexity API errors"""
    pass

def chat_completion_pplx(model, system_message, user_message, response_format=None):
    """
    This function is used to chat with the PPLX API.
    model: The model to use.
    system_message: The system message.
    user_message: The user message.
    response_format: Optional format of the response.
    
    Returns: JSON response from the API
    Raises: PerplexityAPIError if the API call fails
    """
    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY environment variable is not set")
        raise PerplexityAPIError("API key not configured. Please set the PPLX_API_KEY environment variable.")
    
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    
    if response_format:
        payload["response_format"] = response_format

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + PPLX_API_KEY,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        json_response = response.json()
        
        # Validate response structure
        if 'choices' not in json_response or not json_response['choices']:
            logger.error(f"Invalid API response structure: {json_response}")
            raise PerplexityAPIError("Invalid response structure from Perplexity API")
        
        if 'message' not in json_response['choices'][0]:
            logger.error(f"Missing message in API response: {json_response}")
            raise PerplexityAPIError("Missing message in API response")
            
        return json_response
        
    except Timeout:
        logger.error("Request to Perplexity API timed out")
        raise PerplexityAPIError("Request to Perplexity API timed out")
    except HTTPError as e:
        logger.error(f"HTTP error from Perplexity API: {e.response.status_code} - {e.response.text}")
        raise PerplexityAPIError(f"HTTP error from Perplexity API: {e.response.status_code}")
    except RequestException as e:
        logger.error(f"Error making request to Perplexity API: {str(e)}")
        raise PerplexityAPIError(f"Error making request to Perplexity API: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON response from Perplexity API")
        raise PerplexityAPIError("Invalid JSON response from Perplexity API")
    except Exception as e:
        logger.error(f"Unexpected error when calling Perplexity API: {str(e)}")
        raise PerplexityAPIError(f"Unexpected error when calling Perplexity API: {str(e)}")