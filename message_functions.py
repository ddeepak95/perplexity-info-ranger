from urllib.parse import quote
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MessageFormattingError(Exception):
    """Custom exception for message formatting errors"""
    pass

def construct_search_url(query):
    """
    Construct a search URL for Perplexity.
    
    Args:
        query: The search query
        
    Returns:
        str: The formatted search URL
        
    Raises:
        MessageFormattingError: If there's an error formatting the URL
    """
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
            
        website = "https://www.perplexity.ai/search"
        formatted_query = quote(query)
        search_url = f"{website}?q={formatted_query}"
        return search_url
    except Exception as e:
        logger.error(f"Error constructing search URL: {str(e)}")
        raise MessageFormattingError(f"Error constructing search URL: {str(e)}")