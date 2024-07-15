import requests
from dotenv import load_dotenv
import os

load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

def send_html_email(sender_name, to_email, subject, html_content):
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"{sender_name} <noreply@{MAILGUN_DOMAIN}>",
              "to": to_email,
              "subject": subject,
              "html": html_content})
