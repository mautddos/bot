import telebot
import asyncio
from pyrogram import Client

# Replace with your credentials
API_ID = 22625636
API_HASH = "f71778a6e1e102f33ccc4aee3b5cc697"
BOT_TOKEN = "7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE"

# Initialize Telebot & Pyrogram
bot = telebot.TeleBot(BOT_TOKEN)
app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}  # Store user data

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}  # Initialize user data
    bot.send_message(message.chat.id, "Please enter the source channel username (e.g., @channel_name):")
    bot.register_next_step_handler(message, get_source_channel)

def get_source_channel(message):
    source_channel_username = message.text
    user_data[message.chat.id]['source_username'] = source_channel_username

    try:
        source_channel = bot.get_chat(source_channel_username)
        user_data[message.chat.id]['source_id'] = source_channel.id
        bot.send_message(message.chat.id, "Please enter the destination channel ID (e.g., -100123456789):")
        bot.register_next_step_handler(message, get_destination_channel)

    except telebot.apihelper.ApiException as e:
        if "chat not found" in str(e).lower():
            bot.reply_to(message, "Source channel not found. Please enter a valid username.")
            bot.register_next_step_handler(message, get_source_channel)
        else:
            bot.reply_to(message, f"An error occurred: {e}")

def get_destination_channel(message):
    try:
        destination_channel_id = int(message.text)
        user_data[message.chat.id]['destination_id'] = destination_channel_id
        bot.send_message(message.chat.id, "Checking admin permissions...")
        check_admin(message)

    except ValueError:
        bot.reply_to(message, "Invalid destination channel ID. Please enter a valid integer.")
        bot.register_next_step_handler(message, get_destination_channel)

def check_admin(message):
    try:
        bot_user = bot.get_me()
        admins = bot.get_chat_administrators(user_data[message.chat.id]['destination_id'])
        is_admin = any(admin.user.id == bot_user.id for admin in admins)
        
        if is_admin:
            bot.send_message(message.chat.id, "✅ Bot has admin rights. Use /forward_all to start forwarding.")
        else:
            bot.send_message(message.chat.id, "❌ Bot does not have admin rights in the destination channel.")
    except telebot.apihelper.ApiException as e:
        bot.send_message(message.chat.id, f"⚠️ Error checking admin rights: {e}")

async def forward_old_messages(chat_id):
    """Fetch and forward old messages"""
    try:
        async with app:
            source_id = user_data[chat_id]['source_username']
            dest_id = user_data[chat_id]['destination_id']
            async for message in app.get_chat_history(source_id, limit=1000):
                try:
                    if message.text or message.caption or message.media:
                        await app.forward_messages(dest_id, source_id, message.message_id)
                except Exception as e:
                    print(f"⚠️ Error forwarding message {message.message_id}: {e}")
            bot.send_message(chat_id, "✅ Finished forwarding all old messages.")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ An error occurred: {e}")

@bot.message_handler(commands=['forward_all'])
def start_forwarding_all(message):
    if message.chat.id in user_data and 'destination_id' in user_data[message.chat.id]:
        bot.send_message(message.chat.id, "⏳ Forwarding messages. This may take some time...")
        asyncio.create_task(forward_old_messages(message.chat.id))
    else:
        bot.send_message(message.chat.id, "⚠️ Please use /start first to set up the channels.")

def main():
    print("🚀 Bot started...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
