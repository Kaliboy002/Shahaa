import os
import requests
from io import BytesIO
from telethon import TelegramClient, events
from gradio_client import Client, handle_file
from telethon.tl.types import InputMediaPhoto

# Define constants
API_ID = '15787995'  # Your Telegram API ID
API_HASH = 'e51a3154d2e0c45e5ed70251d68382de'  # Your Telegram API Hash
BOT_TOKEN = '7503523093:AAF9QDG8NruQErJ8zugmijmKn57BTcosgW4'  # Your Telegram bot token
IMGBB_API_KEY = 'b34225445e8edd8349d8a9fe68f20369'  # Your ImgBB API Key

# Initialize Gradio client for face-swapping
gradio_client = Client("tuan2308/face-swap")

# Create the Telegram bot client
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to upload image to ImgBB
def upload_to_imgbb(image_bytes):
    url = "https://api.imgbb.com/1/upload"
    files = {'image': ('image.jpg', image_bytes, 'image/jpeg')}
    params = {'key': IMGBB_API_KEY}
    
    response = requests.post(url, files=files, data=params)
    data = response.json()
    if data['success']:
        return data['data']['url']
    else:
        return None

# Event handler for new messages
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome! Please send two images for face swapping.")
    await event.respond("Send the first image.")

# Event handler to receive the first image (source image)
@client.on(events.NewMessage)
async def handle_message(event):
    if event.photo:
        if 'source_image' not in event.data:
            # Get the first image (source image)
            photo = await event.photo.download(file="source_image.jpg")
            event.data['source_image'] = photo
            await event.respond("Got the first image. Now send the second image.")
        else:
            # Get the second image (target image)
            photo = await event.photo.download(file="target_image.jpg")
            event.data['target_image'] = photo
            
            # Perform face swapping using Gradio API
            source_image = event.data['source_image']
            target_image = event.data['target_image']
            
            result = gradio_client.predict(
                source_file=handle_file(source_image),
                target_file=handle_file(target_image),
                doFaceEnhancer=False,
                api_name="/predict"
            )

            swapped_image = result[0]

            # Upload the swapped image to ImgBB
            with open(swapped_image, "rb") as img_file:
                img_bytes = img_file.read()
                swapped_image_url = upload_to_imgbb(img_bytes)
            
            if swapped_image_url:
                await event.respond(f"Here is the swapped face image: {swapped_image_url}")
            else:
                await event.respond("Error uploading the image.")
            
            # Clean up files
            os.remove(source_image)
            os.remove(target_image)
            os.remove(swapped_image)

# Start the bot
client.run_until_disconnected()
