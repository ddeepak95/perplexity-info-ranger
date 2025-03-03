import json
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class JSONProcessingError(Exception):
    """Custom exception for JSON processing errors"""
    pass

def pretty_print(data):
    """
    Pretty print JSON data.
    
    Args:
        data: The data to print
    """
    try:
        print(json.dumps(data, indent=2))
    except Exception as e:
        logger.error(f"Error pretty printing data: {str(e)}")
        print(f"Error formatting data: {str(e)}")
        print(f"Raw data: {data}")

def write_json(data, filename):
    """
    Write data to a JSON file.
    
    Args:
        data: The data to write
        filename: The file to write to
        
    Raises:
        JSONProcessingError: If there's an error writing the file
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully wrote data to {filename}")
    except Exception as e:
        logger.error(f"Error writing JSON to {filename}: {str(e)}")
        raise JSONProcessingError(f"Error writing JSON to {filename}: {str(e)}")

def parse_string_to_json(string):
    """
    Parse a string to JSON.
    
    Args:
        string: The string to parse
        
    Returns:
        dict: The parsed JSON data or None if parsing fails
        
    Raises:
        JSONProcessingError: If there's an error parsing the string
    """
    if not string:
        logger.error("Cannot parse empty string to JSON")
        raise JSONProcessingError("Cannot parse empty string to JSON")
        
    try:
        # Replace single quotes with double quotes
        corrected_string = string.replace("'", '"')
        return json.loads(corrected_string)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise JSONProcessingError(f"Error decoding JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON string: {str(e)}")
        raise JSONProcessingError(f"Unexpected error parsing JSON string: {str(e)}")

def read_json(filename):
    """
    Read data from a JSON file.
    
    Args:
        filename: The file to read from
        
    Returns:
        dict: The parsed JSON data
        
    Raises:
        JSONProcessingError: If there's an error reading the file
    """
    try:
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            raise FileNotFoundError(f"File not found: {filename}")
            
        with open(filename) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {filename}: {e}")
        raise JSONProcessingError(f"Error decoding JSON from {filename}: {e}")
    except Exception as e:
        logger.error(f"Error reading JSON from {filename}: {str(e)}")
        raise JSONProcessingError(f"Error reading JSON from {filename}: {str(e)}")