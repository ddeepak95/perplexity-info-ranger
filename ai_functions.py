import requests
from dotenv import load_dotenv
import os

load_dotenv()

PPLX_API_KEY = os.getenv("PPLX_API_KEY")



def chat_completion_pplx(model, system_message, user_message):
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
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + PPLX_API_KEY,
    }

    response = requests.post(url, json=payload, headers=headers)

    json_response = response.json()

    return json_response