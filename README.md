# Dough

## About

Built with [interactions.py](https://interactions-py.github.io/interactions.py/Guides/).

## Installation

### 1. invite the bot to your server

1. create a discord bot [here](https://discord.com/developers/applications)
2. go to **SETTINGS** > **OAuth2** > **URL Generator**
3. in **SCOPES**, select **bot**
4. in **BOT PERMISSIONS** > **TEXT PERMISSIONS**, select **Send Messages** and **Use Slash Commands**
5. copy the **GENERATED URL** and paste it in your browser
6. copy the **TOKEN** in **SETTINGS** > **Bot** > **Built-A-Bot** > **TOKEN**

### 2. set up the bot locally

1. make sure python 3.10+ is installed
   1. check the version by running `python --version`
   2. if not installed, download it [here](https://www.python.org/downloads/)
2. clone the repository by running `git clone https://github.com/BWsix/dough.git`
3. cd into the directory by running `cd dough`
4. install the dependencies by running `pip install -r requirements.txt`
5. rename `.env.example` to `.env` and paste the **TOKEN** into the file
6. run the bot by running `python main.py`

## Updating

1. cd into the directory by running `cd dough`
2. pull the latest changes by running `git pull`
3. install the dependencies by running `pip install -r requirements.txt`

or

1. execute the update script by running `update`

## Usage

`/upload [image]` - upload rips anonymously
