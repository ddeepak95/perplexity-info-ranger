import datetime
import logging
from message_functions import construct_search_url, MessageFormattingError
from ai_functions import chat_completion_pplx, PerplexityAPIError, chat_completion_openai, OpenAIAPIError
from telegram_functions import send_message_telegram, TelegramAPIError
import asyncio
from config import (
    DAILY_QUERIES, WEEKLY_QUERIES, MONTHLY_QUERIES, CUSTOM_QUERIES, 
    MODEL, SYSTEM_MESSAGE, FORMATTING_MODEL, MAX_RETRIES,
    validate_query_config
)
from pydantic import BaseModel, Field, TypeAdapter
from typing import List
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import model and system message from config
model = MODEL
formatting_model = FORMATTING_MODEL
system_message = SYSTEM_MESSAGE


# Import queries from config
daily_queries = DAILY_QUERIES
weekly_queries = WEEKLY_QUERIES
monthly_queries = MONTHLY_QUERIES

class NewsItem(BaseModel):
    """
    Represents a single news item with title, description, and source link.
    
    This model is used to structure news data retrieved from AI services before
    formatting and sending to Telegram. Each news item represents one piece of news
    that will be displayed to the user.
    """
    title: str = Field(
        description="The headline or title of the news item"
    )
    description: str = Field(
        description="The main content or body of the news item containing details and context"
    )
    link: str = Field(
        description="URL pointing to the source or original article"
    )

class NewsCategory(BaseModel):
    category: str = Field(
        description="The category of the news item"
    )
    news_items: List[NewsItem] = Field(
        description="A list of news items"
    )

class NewsResponse(BaseModel):
    news_items: List[NewsCategory] = Field(
        description="A list of categorized news items"
    )

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


def get_formatted_json_with_ai(content, response_format):
    """
    Format the news content in the given json format using the configured formatting model.
    """
    try:
        completion = chat_completion_openai(
            model=formatting_model,
            system_message="Format the content in the given json format",
            user_message=content,
            response_format=response_format
        )

        logger.info(f"Completion:\n\n{completion}")
        
        # If completion is a string (JSON), parse it directly
        if isinstance(completion, str):
            try:
                parsed_json = json.loads(completion)        
                # Use TypeAdapter to validate and convert to NewsResponse
                response_adapter = TypeAdapter(response_format)
                response = response_adapter.validate_python(parsed_json)
                
                logger.info(f"Successfully parsed JSON string into NewsResponse with {len(response.news_items)} items")
                return response
            except Exception as e:
                logger.error(f"Error parsing JSON string: {str(e)}")
                # Return the original string if parsing fails
                return completion
        else:
            # Handle object response (original implementation)
            response = completion.choices[0].message.parsed
            logger.info(f"Received object response with parsed message")
            return response
            
    except OpenAIAPIError as e:
        logger.error(f"Error formatting content with AI: {str(e)}")
        return content
    except Exception as e:
        logger.error(f"Unexpected error in get_formatted_json_with_ai: {str(e)}")
        return content
    




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
            
            # Get max retries from config or default to 3
            max_retries = MAX_RETRIES
            
            # Try up to max_retries times to get and send a valid response
            for attempt in range(max_retries):
                try:
                    # Get response from AI
                    news_response = chat_completion_pplx(model, system_message, query['description'])
                    news_content = news_response['choices'][0]['message']['content']
                    citations = news_response.get('citations', [])
                
                    
                    # Format message with citations
                    unformatted_message = message + f"{news_content}\n\n"
                    if citations:
                        unformatted_message += "<b>Links:</b>\n"
                        for i, citation in enumerate(citations, 1):
                            unformatted_message += f"[{i}] {citation}\n"

                    logger.info(f"Unformatted message:\n\n{unformatted_message}")

                    # Get formatted JSON response
                    formatted_json = get_formatted_json_with_ai(unformatted_message, NewsResponse)
                    
                    # Construct messages from the JSON response
                    messages_to_send = construct_telegram_messages(formatted_json, query['title'])
                    
                    logger.info(f"Sending {len(messages_to_send)} formatted messages to Telegram")
                    
                    # Send each message separately
                    for i, msg in enumerate(messages_to_send):
                        # Add part number if multiple messages
                        if len(messages_to_send) > 1:
                            msg_with_part = f"Part {i+1}/{len(messages_to_send)}\n\n{msg}"
                        else:
                            msg_with_part = msg
                            
                        # Only include direct_link on the last message instead of the first
                        is_last_message = i == len(messages_to_send) - 1
                        asyncio.run(send_message_telegram(msg_with_part, direct_link if is_last_message else None))
                        logger.info(f"Sent message part {i+1}/{len(messages_to_send)} to Telegram")
                    
                    logger.info(f"Successfully sent all messages to Telegram for {query['title']} on attempt {attempt+1}")
                    break  # Success, exit retry loop
                    
                except PerplexityAPIError as e:
                    logger.error(f"Error getting information from Perplexity AI (attempt {attempt+1}): {str(e)}")
                    if attempt == max_retries - 1:  # Last attempt failed
                        error_message = message + f"⚠️ Error retrieving information: {str(e)}\n\n"
                        error_message += "Please try again later or check your API configuration."
                        asyncio.run(send_message_telegram(error_message, direct_link))
                    else:
                        logger.info(f"Retrying AI request, attempt {attempt+2}/{max_retries}")
                        
                except TelegramAPIError as e:
                    logger.error(f"Error sending message to Telegram (attempt {attempt+1}): {str(e)}")
                    if attempt < max_retries - 1:  # Not the last attempt yet
                        logger.info(f"Telegram error occurred. Retrying with new AI request, attempt {attempt+2}/{max_retries}")
                        # Continue to next iteration which will make a new AI request
                    else:
                        logger.error(f"Failed to send message after {max_retries} attempts")
        
        except Exception as e:
            logger.error(f"Unexpected error processing query '{query['title']}': {str(e)}")
            try:
                error_message = f"⚠️ Error processing query '{query['title']}': {str(e)}\n\nPlease check the logs for more details."
                asyncio.run(send_message_telegram(error_message, ""))
            except Exception as send_error:
                logger.error(f"Failed to send error notification to Telegram: {str(send_error)}")

def construct_telegram_messages(json_response, title, max_message_size=4000):
    """
    Construct multiple Telegram messages from a JSON response if needed due to size limitations.
    
    Args:
        json_response: The formatted JSON response containing categorized news items
        title: The title of the query
        max_message_size: Maximum size of a Telegram message (default 4000 characters)
        
    Returns:
        List of message strings to send
    """
    messages = []
    current_message = f"Here are the top {title} news for you:\n\n"
    current_size = len(current_message)
    
    # If json_response is already a string, try to parse it
    if isinstance(json_response, str):
        try:
            import json
            parsed_json = json.loads(json_response)
            categories = parsed_json.get("news_items", [])
        except Exception as e:
            logger.error(f"Error parsing JSON string: {str(e)}")
            # Return the original string split into chunks if needed
            return split_message(json_response, max_message_size)
    else:
        # If it's already a NewsResponse object
        categories = json_response.news_items
    
    for category in categories:
        # Add category header
        category_header = f"<b><u>📌 {category.category}</u></b>\n\n"
        
        # If adding this category header would exceed the limit, start a new message
        if current_size + len(category_header) > max_message_size:
            messages.append(current_message)
            current_message = category_header
            current_size = len(category_header)
        else:
            current_message += category_header
            current_size += len(category_header)
        
        # Process news items in this category
        for item in category.news_items:
            # Format each news item
            item_text = f"<b>{item.title}</b>\n{item.description}\n{item.link}\n\n"
            item_size = len(item_text)
            
            # If adding this item would exceed the limit, start a new message
            if current_size + item_size > max_message_size:
                messages.append(current_message)
                current_message = item_text
                current_size = item_size
            else:
                current_message += item_text
                current_size += item_size
        current_message += "\n\n"
    
    # Add the last message if it has content
    if current_message:
        messages.append(current_message)
    
    return messages

def split_message(message, max_size=4000):
    """
    Split a message into multiple parts if it exceeds the maximum size.
    
    Args:
        message: The message to split
        max_size: Maximum size of each part
        
    Returns:
        List of message parts
    """
    if len(message) <= max_size:
        return [message]
    
    parts = []
    for i in range(0, len(message), max_size):
        parts.append(message[i:i+max_size])
    
    return parts

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




