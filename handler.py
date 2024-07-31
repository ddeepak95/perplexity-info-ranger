import datetime
import logging
from message_functions import construct_search_url, contruct_news_html_email_content
from ai_functions import chat_completion_pplx
from json_functions import pretty_print, write_json, parse_string_to_json, read_json
from mailgun_functions import send_html_email
from telegram_functions import send_message_telegram, format_news_content_telegram
import asyncio


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
model = "llama-3.1-sonar-large-128k-online"
system_message = "You are an expert researcher. The output should be a json in the format without any other text: [{'title': 'title', 'description': 'description'},...]"
to_email = "ddeepak95@gmail.com"
daily_queries = [
    {"title":"Current Affairs", "description":"Get the top headlines from India and across the world from {yesterday} till {today}. The outputs should not include minor criminal activities and accidents. Be descriptive in the news description. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."},
]
weekly_queries = [
    {"title":"Business and Economy", "description":"Get the top business and economy news {from_last_week}. Be descriptive in the news description. Focus on the major events, trends, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."},
    {"title":"Energy and Climate Change", "description":"Get the top news related to Energy and Climate Change {from_last_week}. Be descriptive in the news description. Focus on the major events, trends, businesses, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics.  Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."},
]
monthly_queries = [
    {"title" : "Investment Opportunities", "description":"Considering the news {from_last_month}, What are the upcoming investment opportunities in India and US with a potential for long-term growth? What are the areas with growing demand and innovation? Focus on sectors such as technology, energy, and consumer goods with a macro-economic perspective. Be descriptive in the description.  Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."}
]

def calculate_past_date(days):
    return (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%b %d, %Y")

def parse_date_keys_to_dates(description):
    today = datetime.datetime.now().strftime("%b %d, %Y")
    yesterday = calculate_past_date(1)
    from_last_week = f"from {calculate_past_date(8)} to {today}"
    from_last_month = f"from {calculate_past_date(32)} to {today}"

    # Dictionary to map placeholders to their corresponding date values
    date_replacements = {
        "{today}": today,
        "{yesterday}": yesterday,
        "{from_last_week}": from_last_week,
        "{from_last_month}": from_last_month
    }

    # Replace the placeholders in the description
    for placeholder, date_value in date_replacements.items():
        description = description.replace(placeholder, date_value)
    
    return description


def research_and_send(queries, query_type):
    todays_date = datetime.datetime.now().strftime("%b %d, %Y")
    for query in queries:
        query["description"] = parse_date_keys_to_dates(query["description"])
        direct_link = construct_search_url(query["description"])
        news_response = chat_completion_pplx(model, system_message, query['description'])
        news_content = parse_string_to_json(news_response['choices'][0]['message']['content']) 
        # Check if the response is in the correct format
        while not isinstance(news_content, list) or not all('title' in item and 'description' in item for item in news_content):
            news_response = chat_completion_pplx(model, system_message, query['description'])
            news_content = parse_string_to_json(news_response['choices'][0]['message']['content'])

        email_content = contruct_news_html_email_content(news_content, direct_link)
        asyncio.run(send_message_telegram(format_news_content_telegram(query["title"], news_content), direct_link))
        send_html_email(query["title"], to_email, f"{query['title']}: {todays_date}", email_content)
        logger.info(f"Sent email for {query['title']}")

def daily_research(event, context):
    research_and_send(daily_queries, "daily")

def weekly_research(event, context):
    research_and_send(weekly_queries, "weekly")

def monthly_research(event, context):
    research_and_send(monthly_queries, "monthly")




