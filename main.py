from telethon import TelegramClient, events
from telethon.tl.types import User
from langdetect import detect
from deep_translator import GoogleTranslator
import textwrap
import os
import requests
import json
import random
import aiohttp
import nextcord
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("WEBHOOK")
appid = os.environ.get("APPID")
apihash = os.environ.get("APIHASH")
apiname = os.environ.get("APINAME")
dlloc = os.environ.get("DLLOC")
input_channels_entities = os.environ.get("INPUT_CHANNELS")
blacklist = os.environ.get("BLACKLIST")
translate = bool(os.environ.get("TRANSLATE"))

if blacklist == 'True':
    blacklist = True

if input_channels_entities is not None:
    input_channels_entities = list(map(int, input_channels_entities.split(',')))

async def imgur(mediafile):
    url = "https://api.imgur.com/3/upload"

    payload = {
        'album': 'ALBUMID',
        'type': 'file',
        'disable_audio': '0'
    }

    files = [
        ('video', open(mediafile, 'rb'))
    ]

    headers = {
        'Authorization': str(random.randint(1, 10000000000))
    }

    response = requests.post(url, headers=headers, data=payload, files=files)
    return json.loads(response.text)

def start():
    client = TelegramClient(apiname, appid, apihash)
    client.start()
    print('Started')
    print(f'Input channels: {input_channels_entities}')
    print(f'Blacklist: {blacklist}')

    @client.on(events.NewMessage(chats=input_channels_entities, blacklist_chats=blacklist))
    async def handler(event):
        if isinstance(event.chat, User):
            return  # Ignore messages from users or bots

        msg = event.message.message

        if translate:
            try:
                if msg != '' and detect(textwrap.wrap(msg, 2000)[0]) != 'en':
                    msg += '\n\n' + 'Translated:\n\n' + GoogleTranslator(source='auto', target='en').translate(msg)
            except:
                pass

        if event.message.sender.username is not None:
            username = event.message.sender.username + ' in ' + event.chat.title
        else:
            username = event.chat.title

        if event.message.media is not None and event.message.file:
            dur = event.message.file.duration
            if dur is None:
                dur = 1

            if dur > 60 or event.message.file.size > 209715201:
                print('Media too long or too big!')
                msg += f"\n\nLink to Video: https://t.me/c/{event.chat.id}/{event.message.id}"
                await send_to_webhook(msg, username)
                return
            else:
                path = await event.message.download_media(dlloc)
                if event.message.file.size > 8388608:
                    await picimgur(path, msg, username)
                else:
                    await pic(path, msg, username)
                os.remove(path)
        else:
            await send_to_webhook(msg, username)

    client.run_until_disconnected()

async def picimgur(filem, message, username):
    async with aiohttp.ClientSession() as session:
        try:
            webhook = nextcord.Webhook.from_url(url, session=session)
            print('Sending w media Imgur')
            try:
                image = await imgur(filem)
                image = image['data']['link']
                print(f'Imgur: {image}')
                await webhook.send(content=image, username=username)
            except Exception as ee:
                print(f'Error {ee.args}')
            for line in textwrap.wrap(message, 2000, replace_whitespace=False):
                await webhook.send(content=line, username=username)
        except Exception as e:
            print(f'Error {e.args}')

async def pic(filem, message, username):
    async with aiohttp.ClientSession() as session:
        try:
            print('Sending w media')
            webhook = nextcord.Webhook.from_url(url, session=session)
            try:
                f = nextcord.File(filem)
                await webhook.send(file=f, username=username)
            except:
                print('Uploading to imgur')
                try:
                    image = await imgur(filem)
                    image = image['data']['link']
                    print(f'Imgur: {image}')
                    await webhook.send(content=image, username=username)
                except Exception as ee:
                    print(f'Error {ee.args}')
            for line in textwrap.wrap(message, 2000, replace_whitespace=False):
                await webhook.send(content=line, username=username)
        except Exception as e:
            print(f'Error {e.args}')

async def send_to_webhook(message, username):
    async with aiohttp.ClientSession() as session:
        print('Sending w/o media')
        webhook = nextcord.Webhook.from_url(url, session=session)
        for line in textwrap.wrap(message, 2000, replace_whitespace=False):
            await webhook.send(content=line, username=username)

if __name__ == "__main__":
    start()
