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
5. rename `.env.example` to `.env` and paste the **TOKEN**, **GUILD_ID** and **CHANNEL_ID** into the file
6. run the bot by running `python main.py`

## Updating

1. cd into the directory by running `cd dough`
2. pull the latest changes by running `git pull`
3. install the dependencies by running `pip install -r requirements.txt`

or

1. open `/scripts` in file explorer and double click `update.bat`

## Running the bot 24/7 in the background

[pm2](https://www.npmjs.com/package/pm2) is a process manager for Node.js applications. It allows you to keep applications alive forever, to reload them without downtime and to facilitate common system admin tasks.

### Installation

1. install pm2 by running `npm install pm2 -g`

### Usage

1. cd into the directory by running `cd dough`
2. start the bot by running `pm2 start main.py --name discord-bot`
3. stop the bot by running `pm2 stop discord-bot`
4. monitor the bot by running `pm2 monit`

or

1. open `/scripts` in file explorer and double click `start.bat` / `stop.bat` / `monitor.bat`

## Bot Usage

(in dm) `/upload [image]` - upload rips anonymously
