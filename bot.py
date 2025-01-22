from telethon import TelegramClient, events
from telethon.tl.types import InputMediaPhoto
from gradio_client import Client, handle_file
import tempfile
import os

# Define your API token and the bot's username
api_id = '15787995'  # Get from https://my.telegram.org/auth
api_hash = 'e51a3154d2e0c45e5ed70251d68382de'  # Get from https://my.telegram.org/auth
bot_token = '7503523093:AAF9QDG8NruQErJ8zugmijmKn57BTcosgW4'  # Your bot token from @BotFather

# Create the Telegram bot client
client = TelegramClient('face_swap_bot', api_id, api_hash).start(bot_token=bot_token)

# Gradio client configuration
gradio_client = Client("tuan2308/face-swap")

async def process_face_swap(source_image_url, target_image_url):
    # Make the prediction with the provided images from URLs
    result = gradio_client.predict(
        source_file=handle_file(source_image_url),
        target_file=handle_file(target_image_url),
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
        
        # Send the result back to the user
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(swapped_image)
            temp_file.close()
            await event.reply(file=temp_file.name)
            os.remove(temp_file.name)  # Clean up the temporary file
    except Exception as e:
        await event.reply(f"Error: {str(e)}")

    # Reset user data
    del user_data.source_image

# Start the bot
client.start()
client.run_until_disconnected()
