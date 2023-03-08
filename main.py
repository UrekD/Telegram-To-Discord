from telethon import TelegramClient, events
import telethon
import aiohttp
import nextcord
from langdetect import detect
from deep_translator import GoogleTranslator
import textwrap
import os
import requests
import json
import random
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("WEBHOOK")
appid = os.environ.get("APPID")
apihash = os.environ.get("APIHASH")
apiname = os.environ.get("APINAME")
dlloc = os.environ.get("DLLOC")
input_channels_entities = os.environ.get("INPUT_CHANNELS")
blacklist = os.environ.get("BLACKLIST")
translate = int(os.environ.get("TRANSLATE"))

if blacklist == 'True':
    blacklist = True
if input_channels_entities is not None:
  input_channels_entities = list(map(int, input_channels_entities.split(',')))

async def imgur(mediafile): # Uploads media to imgur
    url = "https://api.imgur.com/3/upload"

    payload = {'album': 'ALBUMID',
    'type': 'file',
    'disable_audio': '0'}
    files = [
    ('video', open(mediafile,'rb'))
    ]
    headers = {
    'Authorization': str(random.randint(1,10000000000))
    }
    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    return(json.loads(response.text))

def start():
    client = TelegramClient(apiname, 
                            appid, 
                            apihash)
    client.start()
    print('Started')
    print(f'Input channels: {input_channels_entities}')
    print(f'Blacklist: {blacklist}')
    @client.on(events.NewMessage(chats=input_channels_entities, blacklist_chats=blacklist))
    async def handler(event):
        if (type(event.chat)==telethon.tl.types.User):
          return #Ignore Messages from Users or Bots
        msg = event.message.message
        # Try to detect the language and translate the message if it's not english
        if translate:
          try: 
            if msg != '':
                if detect(textwrap.wrap(msg, 2000)[0]) != 'en':
                    msg += '\n\n'+'Translated:\n\n' + GoogleTranslator(source='auto', target='en').translate(msg)
          except:
            pass
        if event.message.media is not None and event.message.file: # If message has media
            dur = event.message.file.duration # Get duration
            if dur is None: # If duration is none
              dur=1 # Set duration to 1
            # If duration is greater than 60 seconds or file size is greater than 200MB Imgur Limit
            if dur>60 or event.message.file.size > 209715201 :  
              print('Media too long or too big!')
              msg +=f"\n\nLink to Video: https://t.me/c/{event.chat.id}/{event.message.id}" 
              await send_to_webhook(msg,event.chat.title)
              return
            else: # Duration less than 60s send media
              path = await event.message.download_media(dlloc)
              if event.message.file.size > 8388608: # If file size is greater than 8MB use Imgur
                await picimgur(path,msg,event.chat.title)
              else:
                await pic(path,msg,event.chat.title)
              os.remove(path)
        else: # No media text message
            await send_to_webhook(msg,event.chat.title)
        
    client.run_until_disconnected()

async def picimgur(filem,message,username): # Send media to webhook with imgur link
    async with aiohttp.ClientSession() as session:
      try:
        webhook = nextcord.Webhook.from_url(url, session=session)
        print('Sending w media Imgur')
        try:
          image = await imgur(filem) # Upload to imgur
          #print(image)
          image = image['data']['link']
          print(f'Imgur: {image}') 
          await webhook.send(content=image,username=username) # Send imgur link to discord
        except Exception as ee:
          print(f'Error {ee.args}') 
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username) 
      except Exception as e:
        print(f'Error {e.args}')

async def pic(filem,message,username): # Send media to webhook
    async with aiohttp.ClientSession() as session:
      try:
        print('Sending w media')
        webhook = nextcord.Webhook.from_url(url, session=session)
        try: # Try sending to discord
          f = nextcord.File(filem)
          await webhook.send(file=f,username=username)
        except: # If it fails upload to imgur
          print('Uploading to imgur')
          try:
            image = await imgur(filem) # Upload to imgur
            #print(image)
            image = image['data']['link']
            print(f'Imgur: {image}') 
            await webhook.send(content=image,username=username) # Send imgur link to discord
          except Exception as ee:
            print(f'Error {ee.args}') 
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username) 
      except Exception as e:
        print(f'Error {e.args}')

async def send_to_webhook(message,username): # Send message to webhook
    async with aiohttp.ClientSession() as session:
        print('Sending w/o media')
        webhook = nextcord.Webhook.from_url(url, session=session)
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username)

if __name__ == "__main__":
    start()