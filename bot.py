import requests
from telethon import TelegramClient, events
from gradio_client import Client, handle_file
import tempfile
import os

# Define your API token and the bot's username
api_id = '15787995'  # Get from https://my.telegram.org/auth
api_hash = 'e51a3154d2e0c45e5ed70251d68382de'  # Get from https://my.telegram.org/auth
bot_token = '7503523093:AAF9QDG8NruQErJ8zugmijmKn57BTcosgW4'  # Your bot token from @BotFather

# ImgBB API key
imgbb_api_key = 'b34225445e8edd8349d8a9fe68f20369'  # Get from https://imgbb.com/

# Gradio client configuration
gradio_client = Client("tuan2308/face-swap")

# Create the Telegram bot client
client = TelegramClient('face_swap_bot', api_id, api_hash).start(bot_token=bot_token)

# Function to upload an image to ImgBB and get the URL
def upload_to_imgbb(image_path):
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, 'rb') as image_file:
        response = requests.post(url, data={
            'key': imgbb_api_key,
        }, files={
            'image': image_file,
        })
    response_data = response.json()
    if response_data['status'] == 'success':
        return response_data['data']['url']
    else:
        raise Exception("ImgBB upload failed")

async def process_face_swap(source_image_path, target_image_path):
    # Open the image files and pass them to the Gradio API
    with open(source_image_path, "rb") as source_file, open(target_image_path, "rb") as target_file:
        # Make the prediction with the provided images
        result = gradio_client.predict(
            source_file=handle_file(source_file),
            target_file=handle_file(target_file),
            doFaceEnhancer=False,
            api_name="/predict"
        )
    return result

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Hello! Please send the URLs for the source and target images.")

@client.on(events.NewMessage(pattern=r'(https?://[^\s]+)'))
async def handle_image_urls(event):
    # Extract URLs from the message
    urls = event.message.text.split()

    if len(urls) != 2:
        await event.reply("Please send exactly two URLs, one for the source image and one for the target image.")
        return

    source_url, target_url = urls

    try:
        # Download the images from the provided URLs
        source_image = download_image_from_url(source_url)
        target_image = download_image_from_url(target_url)

        # Create temporary files to save the downloaded images
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(source_image)
            source_image_path = temp_file.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(target_image)
            target_image_path = temp_file.name

        # Perform face swap
        swapped_image = await process_face_swap(source_image_path, target_image_path)

        # Save the result to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(swapped_image)
            swapped_image_path = temp_file.name

        # Upload the swapped image to ImgBB
        swapped_image_url = upload_to_imgbb(swapped_image_path)

        # Send the swapped image URL to the user
        caption = f"Here is your face-swapped image: {swapped_image_url}"
        await event.reply(caption)

        # Clean up temporary files
        os.remove(source_image_path)
        os.remove(target_image_path)
        os.remove(swapped_image_path)

    except Exception as e:
        await event.reply(f"Error: {str(e)}")

# Helper function to download an image from a URL
def download_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download image from URL: {url}")

# Start the bot
client.start()
client.run_until_disconnected()
