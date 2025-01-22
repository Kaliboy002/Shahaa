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
    await event.reply("Hello! Send me two photos, one as source and one as target, for face swapping.")

@client.on(events.NewMessage(pattern='(.*)', func=lambda e: e.photo))
async def handle_photos(event):
    # Download the photo from Telegram
    photo = await event.download_media()

    # Get the previous photo or start with source image
    user_data = await event.get_sender()
    if not hasattr(user_data, 'source_image'):
        user_data.source_image = photo
        await event.reply("Source image received! Now send the target image.")
        return
    
    target_image_path = photo

    # Call the Gradio face swap API
    try:
        swapped_image = await process_face_swap(user_data.source_image, target_image_path)

        # Save the result to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(swapped_image)
            temp_file.close()

            # Upload the swapped image to ImgBB
            swapped_image_url = upload_to_imgbb(temp_file.name)

            # Send the swapped image URL to the user
            caption = f"Here is your face-swapped image: {swapped_image_url}"
            await event.reply(caption)

            # Clean up the temporary file
            os.remove(temp_file.name)
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

    # Reset user data
    del user_data.source_image

# Start the bot
client.start()
client.run_until_disconnected()
