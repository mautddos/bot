import telebot
import time
import re

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE'

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}  # Store user-specific data

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}  # Initialize user data
    bot.send_message(message.chat.id, "Please enter the source channel username or link (e.g., @channel_name or https://t.me/channel_name):")
    bot.register_next_step_handler(message, get_source_channel)

def get_source_channel(message):
    source_username = message.text.strip()

    # Extract username from a link if provided
    if "t.me/" in source_username:
        match = re.search(r"t\.me/([\w\d_]+)", source_username)
        if match:
            source_username = "@" + match.group(1)

    user_data[message.chat.id]['source_username'] = source_username

    try:
        source_channel = bot.get_chat(source_username)
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
        destination_channel_id = int(message.text.strip())
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
        bot.send_message(message.chat.id, f"Error checking admin rights: {e}")

@bot.message_handler(commands=['forward_all'])
def start_forwarding_all(message):
    if message.chat.id in user_data and 'source_id' in user_data[message.chat.id] and 'destination_id' in user_data[message.chat.id]:
        bot.send_message(message.chat.id, "⏳ Forwarding messages. This may take some time...")
        forward_all_messages(message.chat.id)
    else:
        bot.send_message(message.chat.id, "⚠️ Please use /start first to set up the channels.")

def forward_all_messages(chat_id):
    source_id = user_data[chat_id]['source_id']
    destination_id = user_data[chat_id]['destination_id']
    
    try:
        message_id = 1
        while True:
            try:
                messages = bot.get_chat_history(source_id, limit=1, offset_id=message_id)
                if not messages:
                    bot.send_message(chat_id, "✅ Finished forwarding all messages.")
                    break
                
                for message in messages:
                    bot.forward_message(destination_id, source_id, message.message_id)
                    time.sleep(1)  # Avoid Telegram rate limits
                    message_id = message.message_id

            except telebot.apihelper.ApiException as e:
                if "message to forward not found" in str(e):
                    bot.send_message(chat_id, "✅ Finished forwarding all messages.")
                    break
                else:
                    print(f"Error forwarding message {message_id}: {e}")
                    time.sleep(2)
                    message_id += 1

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ An error occurred: {e}")

def main():
    print("🤖 Bot started...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
