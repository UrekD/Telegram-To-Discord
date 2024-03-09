# <span style="font-size:larger; color:red;">**Note: This project is archived.**</span>

Due to lack of time and myself no longer using it, I'm no longer able to maintain this project. As such, it is now in a read-only state, and no further updates or maintenance will be provided.

If you find this project useful and would like to fork it or take over maintenance, feel free to do so. Thank you to everyone who contributed or used this project over the years.

# Telegram-To-Discord
Mirrors all messages from Telegram and translates them if they are not English and sends them to the webhook with all the media. Only works for photos and videos not longer than 60 seconds (imgur limit) in which case it displays a link to the message in Telegram.

# Requirements

- Python 3.11 or later
- Python pip -> requirements.txt
- Discord bot token
- Telegram API tokens

# How to run
```py
#Download the repo and extract to an empty folder
#Open a CLI ex. CMD,PS,GitBash in the directory
pip3 install -r requirements.txt
#Rename example.env to .env
#Edit info in .env
#APPID and HASH are created here https://core.telegram.org/api/obtaining_api_id
python3 main.py
```
# Example
![image](https://user-images.githubusercontent.com/38784343/186721485-0c1b2393-448a-484d-9ed3-44a30d0d4a8a.png)
