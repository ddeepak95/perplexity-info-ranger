import datetime
import logging
from message_functions import construct_search_url, contruct_news_html_email_content
from ai_functions import chat_completion_pplx
from json_functions import pretty_print, write_json, parse_string_to_json, read_json
from mailgun_functions import send_html_email


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
model = "llama-3-sonar-large-32k-online"
system_message = "You are an expert researcher. The output should be a json in the format without any other text: [{'title': 'title', 'description': 'description'},...]"
to_email = "ddeepak95@gmail.com"
daily_queries = [
    {"title":"Current Affairs", "description":"Get the top headlines from India and across the world from yesterday till today. The outputs should not include minor criminal activities and accidents. Be descriptive in the news description."},
]
weekly_queries = [
    {"title":"Business and Economy", "description":"Get the top business and economy news from the past week. Be descriptive in the news description. Focus on the major events, trends, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics."},
    {"title":"Energy and Climate Change", "description":"Get the top news related to Energy and Climate Change from the past week. Be descriptive in the news description. Focus on the major events, trends, businesses, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics."},
]
monthly_queries = [
    {"title" : "Investment Opportunities", "description":"What are the upcoming investment opportunities in India and US with a potential for long-term growth? What are the areas with growing demand and innovation? Focus on sectors such as technology, energy, and consumer goods with a macro-economic perspective. Be descriptive in the description."}
]

def send_research_emails(queries, query_type):
    todays_date = datetime.datetime.now().strftime("%b %d, %Y")
    for query in queries:
        direct_link = construct_search_url(query["description"])
        news_response = chat_completion_pplx(model, system_message, query['description'])
        news_content = parse_string_to_json(news_response['choices'][0]['message']['content'])
        # Check if the response is in the correct format
        while not isinstance(news_content, list) or not all('title' in item and 'description' in item for item in news_content):
            news_response = chat_completion_pplx(model, system_message, query['description'])
            news_content = parse_string_to_json(news_response['choices'][0]['message']['content'])

        email_content = contruct_news_html_email_content(news_content, direct_link)
        send_html_email(query["title"], to_email, f"{query['title']}: {todays_date}", email_content)
        logger.info(f"Sent email for {query['title']}")

def daily_research(event, context):
    send_research_emails(daily_queries, "daily")

def weekly_research(event, context):
    send_research_emails(weekly_queries, "weekly")

def monthly_research(event, context):
    send_research_emails(monthly_queries, "monthly")

