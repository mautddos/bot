import telebot

# Replace with your actual bot token
BOT_TOKEN = '7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE'

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}  # Store user-specific data

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}  # Initialize user data
    bot.send_message(message.chat.id, "Please enter the source channel username (e.g., @channel_name or https://t.me/channel_name):")
    bot.register_next_step_handler(message, get_source_channel)

def get_source_channel(message):
    source_username = message.text.strip()

    # Extract username from link if needed
    if "t.me/" in source_username:
        source_username = "@" + source_username.split("/")[-1]

    user_data[message.chat.id]['source_username'] = source_username

    try:
        source_channel = bot.get_chat(source_username)
        user_data[message.chat.id]['source_id'] = source_channel.id
        bot.send_message(message.chat.id, "Please enter the destination channel ID (e.g., -100123456789):")
        bot.register_next_step_handler(message, get_destination_channel)

    except telebot.apihelper.ApiException as e:
        bot.reply_to(message, "⚠️ Source channel not found. Please enter a valid username.")
        bot.register_next_step_handler(message, get_source_channel)

def get_destination_channel(message):
    try:
        destination_channel_id = int(message.text.strip())
        user_data[message.chat.id]['destination_id'] = destination_channel_id
        bot.send_message(message.chat.id, "🔍 Checking admin permissions...")
        check_admin(message)

    except ValueError:
        bot.reply_to(message, "⚠️ Invalid destination channel ID. Please enter a valid number.")
        bot.register_next_step_handler(message, get_destination_channel)

def check_admin(message):
    try:
        bot_user = bot.get_me()
        admins = bot.get_chat_administrators(user_data[message.chat.id]['destination_id'])
        is_admin = any(admin.user.id == bot_user.id for admin in admins)

        if is_admin:
            bot.send_message(message.chat.id, "✅ Bot has admin rights. It will now forward new messages automatically.")
        else:
            bot.send_message(message.chat.id, "❌ Bot is NOT an admin in the destination channel. Please grant admin permissions.")

    except telebot.apihelper.ApiException as e:
        bot.send_message(message.chat.id, f"⚠️ Error checking admin rights: {e}")

@bot.channel_post_handler(func=lambda m: True)
def forward_new_messages(message):
    """ Forward only new messages when they arrive in the source channel """
    for chat_id in user_data:
        if 'source_id' in user_data[chat_id] and user_data[chat_id]['source_id'] == message.chat.id:
            if 'destination_id' in user_data[chat_id]:
                destination_id = user_data[chat_id]['destination_id']
                bot.forward_message(destination_id, message.chat.id, message.message_id)

def main():
    print("🤖 Bot started...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()
