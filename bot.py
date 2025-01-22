import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import states
from gradio_client import Client, handle_file
import tempfile
import os

API_TOKEN = '7503523093:AAF9QDG8NruQErJ8zugmijmKn57BTcosgW4'  # Replace with your Telegram bot token

# Gradio client configuration
client = Client("tuan2308/face-swap")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(states.State):
    source_image = states.State()
    target_image = states.State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Welcome! Please send the source image.")
    await Form.source_image.set()

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=Form.source_image)
async def process_source_image(message: types.Message, state: FSMContext):
    photo = message.photo[-1]  # Get the highest resolution photo
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, 'source_image.jpg')
    
    await state.update_data(source_image='source_image.jpg')
    await message.reply("Got it! Now send the target image.")
    await Form.next()

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=Form.target_image)
async def process_target_image(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    source_image_path = user_data.get('source_image')

    target_photo = message.photo[-1]
    target_file_id = target_photo.file_id
    target_file = await bot.get_file(target_file_id)
    await bot.download_file(target_file.file_path, 'target_image.jpg')

    # Prepare the file paths for swapping
    target_image_path = 'target_image.jpg'
    
    # Make the prediction with the provided images
    try:
        result_image = client.predict(
            source_file=handle_file(source_image_path),
            target_file=handle_file(target_image_path),
            doFaceEnhancer=False,
            api_name="/predict"
        )

        # Assuming the result is a URL or image file path, send it to the user
        if isinstance(result_image, str):
            # If the result is a URL, send the image directly
            await message.reply(f"Here is the result: {result_image}")
        elif isinstance(result_image, bytes):
            # If the result is image data, save it to a temporary file and send it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(result_image)
                temp_file_path = temp_file.name
                await bot.send_photo(message.chat.id, photo=open(temp_file_path, 'rb'))
                os.remove(temp_file_path)

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

    await state.finish()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
