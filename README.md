# Reminder Bot

Reminder Bot is a Discord bot designed to help users set and manage reminders. It is built using the `discord.py` library and interacts with a MongoDB database for storing reminder data.

# Invite Bot
[![Static Badge](https://img.shields.io/badge/Add%20Bot-blue?logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1309446419475730502)


## Features

- Set reminders with custom messages
- Manage and delete existing reminders
- Developer commands for managing the bot

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/reminder-bot.git
    cd reminder-bot
    ```

2. Create a virtual environment and activate it:
    
    * Linux
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```
    * Windows
    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Copy the example environment file and configure it:
    ```sh
    cp example.env .env
    ```

5. Fill in the `.env` file with your Discord bot token and MongoDB connection URL.

## Usage

1. Run the bot:
    ```sh
    python main.py
    ```

2. The bot will log in and start listening for commands.

## Commands

### User Commands

- `/setreminder <time> <message>`: Set a reminder.
- `/deletereminder <id>`: Delete a reminder.

### Developer Commands

- `/dev reload <cog>`: Reload a cog.
- `/dev sync`: Sync the commands with Discord.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.
