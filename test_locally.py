#!/usr/bin/env python
"""
Test script to run the Info Ranger functions locally.
This helps verify that your setup is working correctly before deployment.
"""

import sys
import importlib
from handler import daily_research, weekly_research, monthly_research
from config import CUSTOM_QUERIES

def print_usage():
    print("Usage: python test_locally.py [daily|weekly|monthly|custom:<name>|list]")
    print("Examples:")
    print("  python test_locally.py daily       # Run daily research")
    print("  python test_locally.py weekly      # Run weekly research")
    print("  python test_locally.py monthly     # Run monthly research")
    print("  python test_locally.py custom:tech_news  # Run a custom query named 'tech_news'")
    print("  python test_locally.py list        # List all available custom queries")

def list_custom_queries():
    """List all available custom queries from config.py"""
    if not CUSTOM_QUERIES:
        print("No custom queries defined in config.py")
        return
    
    print("\nAvailable custom queries:")
    print("-" * 50)
    for i, query in enumerate(CUSTOM_QUERIES, 1):
        print(f"{i}. {query['name']} - {query['title']}")
        print(f"   Schedule: {query['cron']}")
        print(f"   Description: {query['description'][:60]}..." if len(query['description']) > 60 else f"   Description: {query['description']}")
        print()

def run_custom_query(query_name):
    """Run a specific custom query by name"""
    # Find the query in CUSTOM_QUERIES
    query_config = None
    for query in CUSTOM_QUERIES:
        if query['name'] == query_name:
            query_config = query
            break
    
    if not query_config:
        print(f"Error: Custom query '{query_name}' not found in config.py")
        print("Use 'python test_locally.py list' to see all available custom queries")
        return False
    
    print(f"Running custom query: {query_config['title']} ({query_name})")
    
    # Import the handler module to get the dynamically created function
    # We need to reload the module to ensure we get the latest version with all dynamic functions
    import handler as handler_module
    importlib.reload(handler_module)
    
    # Check if the function exists in the handler module
    if hasattr(handler_module, query_name):
        # Call the function
        custom_function = getattr(handler_module, query_name)
        custom_function(None, None)
        print(f"Custom query '{query_name}' completed!")
        return True
    else:
        # If the function doesn't exist yet, we'll create it temporarily for testing
        from handler import generate_custom_research_function
        custom_function = generate_custom_research_function(query_config)
        custom_function(None, None)
        print(f"Custom query '{query_name}' completed!")
        return True

def main():
    if len(sys.argv) != 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_custom_queries()
        return
    
    if command.startswith("custom:"):
        query_name = command.split(":", 1)[1]
        run_custom_query(query_name)
        return
    
    print(f"Running {command} research function...")
    
    if command == "daily":
        daily_research(None, None)
        print("Daily research completed!")
    elif command == "weekly":
        weekly_research(None, None)
        print("Weekly research completed!")
    elif command == "monthly":
        monthly_research(None, None)
        print("Monthly research completed!")
    else:
        print(f"Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main() 