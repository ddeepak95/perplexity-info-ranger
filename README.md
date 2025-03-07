# Perplexity Info Ranger

Perplexity Info Ranger is an automated news curation and research tool that uses Perplexity AI to gather relevant news and information on various topics from the web and sends them to a Telegram channel. The tool also uses OpenAI to format the news content into structured, readable messages. The application runs as a serverless function on AWS Lambda, scheduled to execute at specific intervals.

## Example Screenshot

<img src="https://i.imgur.com/FrhPQXW.jpeg" alt="Perplexity Info Ranger Screenshot" width="300" />

## Features

- **Daily Updates**: Automatically collect information on your chosen topics every day
- **Weekly Digests**: Gather weekly summaries or reports on specified subjects
- **Monthly Insights**: Obtain comprehensive monthly analyses on topics of interest
- **Custom Frequency**: Define your own schedules for specialized information needs
- **AI-Powered Research**: Leverage Perplexity AI to gather comprehensive and relevant information
- **Structured News Format**: News is organized by categories with titles, descriptions, and source links
- **Smart Formatting**: Uses OpenAI to format news content into structured, readable messages
- **Message Size Management**: Automatically splits large messages for Telegram's character limits
- **Automated Delivery**: Send formatted results directly to your Telegram channel
- **Serverless Architecture**: Run on AWS Lambda with minimal maintenance and operational costs
- **Fully Customizable**: Easily add, modify, or remove topics and adjust scheduling to suit your needs

## Project Structure

```
info-ranger/
├── .env                    # Environment variables (not to be committed to version control)
├── .env.example            # Example environment variables file
├── .gitignore              # Git ignore file
├── ai_functions.py         # Functions for interacting with Perplexity AI API
├── config.py               # Configuration file for queries and schedules
├── generate_serverless_config.py # Script to update serverless.yml with custom queries
├── handler.py              # Main Lambda handler functions
├── json_functions.py       # Utility functions for JSON operations
├── message_functions.py    # Functions for message formatting
├── package.json            # Node.js package configuration
├── requirements.txt        # Python dependencies
├── serverless.yml          # Serverless Framework configuration
├── test_locally.py         # Script to test functions locally
└── telegram_functions.py   # Functions for sending messages to Telegram
```

## Prerequisites

- [Node.js](https://nodejs.org/) (v14 or later)
- [Python](https://www.python.org/) (3.10)
- [Serverless Framework](https://www.serverless.com/) CLI
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- Perplexity AI API key
- OpenAI API key
- Telegram Bot Token and Channel ID (Refer to the [Telegram Bot and Channel](#telegram-bot-and-channel) section for how to get them)

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install Serverless Framework and plugins**

   ```bash
   npm install -g serverless
   npm install
   ```

3. **Create a Python virtual environment and install dependencies**

   ```bash
   # For Windows
   python -m venv .venv
   .venv\Scripts\activate

   # For macOS/Linux
   python -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root with the following variables:

   ```
   PPLX_API_KEY=your_perplexity_ai_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Configure AWS credentials**

   Make sure your AWS credentials are configured. You can do this by running:

   ```bash
   aws configure
   ```

## Deployment

1. **Update the serverless.yml configuration**

   After adding custom queries, run the generator script to update your serverless.yml:

   ```bash
   python generate_serverless_config.py
   ```

   Ensure that the org is set to your AWS account name.

2. **Deploy to AWS using Serverless Framework**

   ```bash
   serverless deploy
   ```

   This will deploy the application to AWS Lambda with the configured schedules.

3. **Verify deployment**

   After deployment, you should see output with details about the deployed functions and endpoints.

## Customization

### Customizing Queries and Schedules

The project is designed to be easily customizable. You can modify existing queries or add your own custom queries with different schedules:

1. **Edit the `config.py` file**

   This file contains all the query configurations:

   - `DAILY_QUERIES`: Run every day
   - `WEEKLY_QUERIES`: Run once a week
   - `MONTHLY_QUERIES`: Run once a month
   - `CUSTOM_QUERIES`: Define your own custom queries with custom schedules

2. **Adding a Custom Query**

   To add a custom query with a custom schedule, add an entry to the `CUSTOM_QUERIES` list in `config.py`:

   ```python
   CUSTOM_QUERIES = [
       {
           "name": "tech_news",  # This will be the function name
           "title": "Technology News",
           "description": "Get the latest technology news and innovations {from_last_week}. Focus on AI, blockchain, and emerging technologies.",
           "cron": "cron(0 12 ? * WED *)"  # Run every Wednesday at 12:00 UTC
       },
       # Add more custom queries here
   ]
   ```

3. **Update the serverless.yml configuration**

   After adding custom queries, run the generator script to update your serverless.yml:

   ```bash
   python generate_serverless_config.py
   ```

4. **Deploy your changes**

   ```bash
   serverless deploy
   ```

### Understanding Cron Expressions

AWS Lambda uses cron expressions to schedule functions. Here's how to define them:

```
cron(minute hour day-of-month month day-of-week year)
```

Examples:

- `cron(0 10 * * ? *)`: Run at 10:00 AM UTC every day
- `cron(0 12 ? * MON *)`: Run at 12:00 PM UTC every Monday
- `cron(0 15 1 * ? *)`: Run at 3:00 PM UTC on the 1st of every month

For more information, see [AWS Cron Expression Reference](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html).

### Date Placeholders

You can use the following placeholders in your query descriptions:

- `{today}`: Current date (e.g., "Aug 15, 2023")
- `{yesterday}`: Yesterday's date
- `{from_last_week}`: Date range from 8 days ago to today
- `{from_last_month}`: Date range from 32 days ago to today

### Modifying the AI Models

You can change the AI models used by modifying these variables in `config.py`:

- `MODEL`: The main model used for gathering news information (Perplexity AI)
- `FORMATTING_MODEL`: The model used for formatting news content into structured JSON (OpenAI)
- `SYSTEM_MESSAGE`: The system prompt that guides the AI's response style

### News Formatting

The application formats news into a structured format with:

- Categories of news (e.g., "Technology", "Business", "Science")
- Individual news items within each category containing:
  - Title: The headline of the news
  - Description: A summary or details about the news
  - Link: Source URL for the news item

This structured format makes the news easier to read and navigate in Telegram messages.

## Testing Locally

You can test the functions locally before deployment:

```bash
# Test daily research function
python test_locally.py daily

# Test weekly research function
python test_locally.py weekly

# Test monthly research function
python test_locally.py monthly

# List all available custom queries
python test_locally.py list

# Test a specific custom query
python test_locally.py custom:tech_news
```

This allows you to verify that your queries are working correctly before deploying them to AWS Lambda.

## Obtaining Required API Keys and IDs

### Perplexity AI API Key

1. Sign up at [Perplexity AI](https://www.perplexity.ai/)
2. Navigate to your account settings to generate an API key

### Telegram Bot and Channel

1. Create a Telegram bot using [BotFather](https://t.me/botfather)
2. Note the bot token provided by BotFather
3. Create a Telegram channel
4. Add your bot to the channel as an administrator
5. Get the channel ID by forwarding a message from the channel to [@userinfobot](https://t.me/userinfobot)

## Troubleshooting

- **Deployment Issues**: Ensure AWS credentials are correctly configured
- **Function Timeouts**: If functions time out, increase the `timeout` value in `serverless.yml`
- **Missing Dependencies**: Make sure all dependencies are listed in `requirements.txt`
- **Telegram Errors**: Verify the bot has proper permissions in the channel
- **Custom Query Not Running**: Check that the cron expression is valid and that the function was added to serverless.yml
- **Formatting Issues**: If news isn't formatting correctly, check the `FORMATTING_MODEL` configuration and ensure your OpenAI API key is valid
- **Message Size Errors**: If you receive errors about message size, the application will automatically split messages, but you may need to adjust your queries to return less content

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
