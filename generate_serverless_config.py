#!/usr/bin/env python
"""
Script to generate serverless.yml configuration for custom queries.
This helps users easily add their own custom queries with custom schedules.
"""

import sys
import yaml
from config import CUSTOM_QUERIES

def generate_serverless_config():
    """Generate serverless.yml configuration with custom queries"""
    
    # Load existing serverless.yml
    try:
        with open('serverless.yml', 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: serverless.yml not found. Make sure you're in the project root directory.")
        sys.exit(1)
    
    # Check if there are any custom queries
    if not CUSTOM_QUERIES:
        print("No custom queries found in config.py. Add some queries to CUSTOM_QUERIES first.")
        return
    
    # Add custom queries to functions
    for query in CUSTOM_QUERIES:
        function_name = query["name"]
        
        # Skip if function already exists
        if function_name in config.get('functions', {}):
            print(f"Function '{function_name}' already exists in serverless.yml. Skipping.")
            continue
        
        # Add function configuration
        config['functions'][function_name] = {
            'handler': f'handler.{function_name}',
            'timeout': 900,
            'events': [
                {'schedule': query['cron']}
            ]
        }
        
        print(f"Added function '{function_name}' with schedule: {query['cron']}")
    
    # Write updated configuration back to serverless.yml
    with open('serverless.yml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
    
    print("\nServerless configuration updated successfully!")
    print("To deploy your changes, run: serverless deploy")

if __name__ == "__main__":
    print("Generating serverless configuration for custom queries...")
    generate_serverless_config() 