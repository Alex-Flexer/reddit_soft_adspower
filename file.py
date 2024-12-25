from aiogram import Bot, Dispatcher, types
import asyncio

API_TOKEN = '8078572509:AAHT8WKFdUmViX_LC9_qRRebtsVpPxtkPN4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Define a new keyboard layout
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton('Button 1'))
keyboard.add(types.KeyboardButton('Button 2'))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Send a message with a keyboard layout
    msg = await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.", reply_markup=keyboard)
    
    # Store the message ID
    message_id = msg.message_id
    
    # Edit the message's reply markup after 5 seconds
    await asyncio.sleep(5)
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=None)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stdout)
    asyncio.run(main())
