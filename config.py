"""
Configuration file for Info Ranger queries and schedules.
Users can easily modify this file to add, remove, or change queries and their frequency.
"""

# Query configurations
# Format: Each query is a dictionary with 'title' and 'description' keys
# The description can include date placeholders: {today}, {yesterday}, {from_last_week}, {from_last_month}
# These will be automatically replaced with the appropriate dates when the query runs

# Daily queries - Run every day
DAILY_QUERIES = [
    {
        "title": "Current Affairs",
        "description": "Get the top headlines from India, US and the world for {today}. The news should cover politics, economy, sports, entertainment, and technology. The outputs should not include minor criminal activities and minor accidents. Be descriptive in the news description. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."
    },
    # Add more daily queries here
]

# Weekly queries - Run once a week
WEEKLY_QUERIES = [
    {
        "title": "Business and Economy",
        "description": "Get the top business and economy news {from_last_week}. Be descriptive in the news description. Focus on the major events, trends, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."
    },
    {
        "title": "Energy and Climate Change",
        "description": "Get the top news related to Energy and Climate Change {from_last_week}. Be descriptive in the news description. Focus on the major events, trends, businesses, and macro-economic happenings that could be useful for an investor. Focus on India and US demographics. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."
    },
    # Add more weekly queries here
]

# Monthly queries - Run once a month
MONTHLY_QUERIES = [
    {
        "title": "Investment Opportunities",
        "description": "Considering the news {from_last_month}, What are the upcoming investment opportunities in India and US with a potential for long-term growth? What are the areas with growing demand and innovation? Focus on sectors such as technology, energy, and consumer goods with a macro-economic perspective. Be descriptive in the description. Include the date in which the news got published in the description. Don't include any news outside the date frame in the prompt."
    },
    # Add more monthly queries here
]

# Custom queries - Define your own frequency
# These will need to be manually added to serverless.yml
CUSTOM_QUERIES = [
    # Example of a custom query that runs every Wednesday at 12:00 UTC
    {
        "name": "tech_news",  # This will be the function name in serverless.yml
        "title": "Technology News",
        "description": "Get the latest technology news and innovations {from_last_week}. Focus on AI, blockchain, and emerging technologies.",
        "cron": "cron(0 12 ? * WED *)"  # Run every Wednesday at 12:00 UTC
    },
    # Example of a custom query that runs every Monday and Thursday at 15:00 UTC
    {
        "name": "crypto_updates",
        "title": "Cryptocurrency Updates",
        "description": "Get the latest cryptocurrency market updates and news {from_last_week}. Focus on Bitcoin, Ethereum, and other major cryptocurrencies.",
        "cron": "cron(0 15 ? * MON,THU *)"  # Run every Monday and Thursday at 15:00 UTC
    },
    # Add more custom queries here as needed
]

# AI Model configuration
MODEL = "sonar-reasoning-pro"
FORMATTING_MODEL = "gpt-4o"

# System message for the AI
SYSTEM_MESSAGE = """You are an expert news curator and researcher. You have to find the most relevant news for the user. Include at least 8 news items in your response. Do not hallucinate and include news that are not present in the requested date range.
Please output in the following format. Do not include any other text in your response.

<b><i>Sub Topic 1</i></b>

<b>Title 1</b>
Description 1

<b>Title 2</b>
Description 2

...
"""

MAX_RETRIES = 3



# Configuration validation
def validate_query_config(query, query_type):
    """
    Validate a query configuration.
    
    Args:
        query: The query configuration to validate
        query_type: The type of query (daily, weekly, monthly, custom)
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check required fields
    if not isinstance(query, dict):
        print(f"Error: {query_type} query must be a dictionary")
        return False
        
    if 'title' not in query:
        print(f"Error: {query_type} query missing 'title' field")
        return False
        
    if 'description' not in query:
        print(f"Error: {query_type} query missing 'description' field")
        return False
        
    # For custom queries, check additional required fields
    if query_type == 'custom':
        if 'name' not in query:
            print(f"Error: Custom query missing 'name' field")
            return False
            
        if 'cron' not in query:
            print(f"Error: Custom query missing 'cron' field")
            return False
            
        # Validate function name (should be a valid Python identifier)
        if not query['name'].isidentifier():
            print(f"Error: Custom query name '{query['name']}' is not a valid Python identifier")
            return False
    
    return True

def validate_all_configs():
    """
    Validate all query configurations.
    
    Returns:
        bool: True if all configurations are valid, False otherwise
    """
    all_valid = True
    
    # Validate daily queries
    for i, query in enumerate(DAILY_QUERIES):
        if not validate_query_config(query, 'daily'):
            print(f"Invalid daily query at index {i}: {query}")
            all_valid = False
    
    # Validate weekly queries
    for i, query in enumerate(WEEKLY_QUERIES):
        if not validate_query_config(query, 'weekly'):
            print(f"Invalid weekly query at index {i}: {query}")
            all_valid = False
    
    # Validate monthly queries
    for i, query in enumerate(MONTHLY_QUERIES):
        if not validate_query_config(query, 'monthly'):
            print(f"Invalid monthly query at index {i}: {query}")
            all_valid = False
    
    # Validate custom queries
    for i, query in enumerate(CUSTOM_QUERIES):
        if not validate_query_config(query, 'custom'):
            print(f"Invalid custom query at index {i}: {query}")
            all_valid = False
    
    return all_valid

# Validate configurations when module is imported
if __name__ != "__main__":
    validate_all_configs() 