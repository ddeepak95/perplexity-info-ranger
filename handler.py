import datetime
import logging
from message_functions import construct_search_url, MessageFormattingError
from ai_functions import chat_completion_pplx, PerplexityAPIError
from telegram_functions import send_message_telegram, TelegramAPIError
import asyncio
from config import DAILY_QUERIES, WEEKLY_QUERIES, MONTHLY_QUERIES, CUSTOM_QUERIES, MODEL, SYSTEM_MESSAGE, validate_query_config


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import model and system message from config
model = MODEL
system_message = SYSTEM_MESSAGE

# Import queries from config
daily_queries = DAILY_QUERIES
weekly_queries = WEEKLY_QUERIES
monthly_queries = MONTHLY_QUERIES

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
    """
    Research topics using Perplexity AI and send results to Telegram.
    
    Args:
        queries: List of query configurations
        query_type: Type of query (daily, weekly, monthly, custom)
    """
    if not queries:
        logger.warning(f"No {query_type} queries configured")
        return
        
    for query in queries:
        try:
            # Validate query configuration
            if not validate_query_config(query, query_type):
                logger.error(f"Invalid {query_type} query configuration: {query}")
                continue
                
            logger.info(f"Processing {query_type} query: {query['title']}")
            
            message = f"Here are the top {query['title']} news for you:\n\n"
            query["description"] = parse_date_keys_to_dates(query["description"])
            
            try:
                direct_link = construct_search_url(query["description"])
            except MessageFormattingError as e:
                logger.error(f"Error constructing search URL: {str(e)}")
                direct_link = "https://www.perplexity.ai/"
                message += f"⚠️ Error creating direct link: {str(e)}\n\n"
            
            try:
                news_response = chat_completion_pplx(model, system_message, query['description'])
                news_content = news_response['choices'][0]['message']['content']
                citations = news_response.get('citations', [])
            except PerplexityAPIError as e:
                logger.error(f"Error getting information from Perplexity AI: {str(e)}")
                message += f"⚠️ Error retrieving information: {str(e)}\n\n"
                message += "Please try again later or check your API configuration."
                asyncio.run(send_message_telegram(message, direct_link))
                continue

            # Format message with citations
            message += f"{news_content}\n\n"
            if citations:
                message += "Links:\n"
                for i, citation in enumerate(citations, 1):
                    message += f"{i}. {citation}\n"

            try:
                asyncio.run(send_message_telegram(message, direct_link))
                logger.info(f"Successfully sent message to Telegram for {query['title']}")
            except TelegramAPIError as e:
                logger.error(f"Error sending message to Telegram: {str(e)}")
                # We can't notify the user if Telegram is down, so just log the error
        
        except Exception as e:
            logger.error(f"Unexpected error processing query '{query['title']}': {str(e)}")
            try:
                error_message = f"⚠️ Error processing query '{query['title']}': {str(e)}\n\nPlease check the logs for more details."
                asyncio.run(send_message_telegram(error_message, ""))
            except Exception as send_error:
                logger.error(f"Failed to send error notification to Telegram: {str(send_error)}")

def daily_research(event, context):
    """Lambda handler for daily research queries"""
    try:
        logger.info("Starting daily research")
        research_and_send(daily_queries, "daily")
        return {"statusCode": 200, "body": "Daily research completed successfully"}
    except Exception as e:
        logger.error(f"Error in daily research: {str(e)}")
        return {"statusCode": 500, "body": f"Error in daily research: {str(e)}"}

def weekly_research(event, context):
    """Lambda handler for weekly research queries"""
    try:
        logger.info("Starting weekly research")
        research_and_send(weekly_queries, "weekly")
        return {"statusCode": 200, "body": "Weekly research completed successfully"}
    except Exception as e:
        logger.error(f"Error in weekly research: {str(e)}")
        return {"statusCode": 500, "body": f"Error in weekly research: {str(e)}"}

def monthly_research(event, context):
    """Lambda handler for monthly research queries"""
    try:
        logger.info("Starting monthly research")
        research_and_send(monthly_queries, "monthly")
        return {"statusCode": 200, "body": "Monthly research completed successfully"}
    except Exception as e:
        logger.error(f"Error in monthly research: {str(e)}")
        return {"statusCode": 500, "body": f"Error in monthly research: {str(e)}"}

# Dynamic function generator for custom queries
def generate_custom_research_function(query_config):
    """Generate a custom research function based on the provided configuration"""
    def custom_research(event, context):
        try:
            logger.info(f"Starting custom research: {query_config['title']}")
            research_and_send([{"title": query_config["title"], "description": query_config["description"]}], "custom")
            return {"statusCode": 200, "body": f"Custom research '{query_config['title']}' completed successfully"}
        except Exception as e:
            logger.error(f"Error in custom research '{query_config['title']}': {str(e)}")
            return {"statusCode": 500, "body": f"Error in custom research '{query_config['title']}': {str(e)}"}
    return custom_research

# Dynamically create custom research functions
for custom_query in CUSTOM_QUERIES:
    function_name = custom_query["name"]
    globals()[function_name] = generate_custom_research_function(custom_query)




