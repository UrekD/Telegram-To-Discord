from telethon import TelegramClient, events
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
    #input_channels_entities = [-1336211109]
    #output_channel_entities = []
    print('Started')
    
    @client.on(events.NewMessage())
    async def handler(event):
        #print(event.chat)
        #print(event.message)
        msg = event.message.message
        # Try to detect the language and translate the message if it's not english
        try: 
          if msg != '':
              if detect(textwrap.wrap(msg, 2000)[0]) != 'en':
                  msg += '\n\n'+'Translated:\n\n' + GoogleTranslator(source='auto', target='en').translate(msg)
         # print(mm)
        except:
          pass
        # Check if the message is has a media file
        if event.message.media is not None:
            dur = 0
            # Set duration to 1 if media has no duration ex. photo
            if event.message.file.duration is None:
              dur=1
            # Duration less than 60s
            if dur>60: # Duration greater than 60s send link to media
              print('Media too long!')
              msg +=f"\n\nLink to Video: https://t.me/c/{event.chat.id}/{event.message.id}" 
              await send_to_webhook(msg,event.chat.title)
              return
            else: # Duration less than 60s send media
              path = await event.message.download_media(dlloc)
              await pic(path,msg,event.chat.title)
              os.remove(path)
        else: # No media text message
            await send_to_webhook(msg,event.chat.title)
        
    client.run_until_disconnected()

async def pic(filem,message,username): # Send media to webhook
    async with aiohttp.ClientSession() as session:
        print('Sending w media')
        webhook = nextcord.Webhook.from_url(url, session=session)
        try: # Try sending to discord
          f = nextcord.File(filem)
          await webhook.send(file=f,username=username)
        except: # If it fails upload to imgur
          print('File too big..')
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

async def send_to_webhook(message,username): # Send message to webhook
    async with aiohttp.ClientSession() as session:
        print('Sending w/o media')
        webhook = nextcord.Webhook.from_url(url, session=session)
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username)

if __name__ == "__main__":
    start()