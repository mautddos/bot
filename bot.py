from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# --- BOT CONFIGURATION ---
BOT_TOKEN = "7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE"
DESTINATION_CHANNEL = "@aaannndndjdhwuwhwvsw92iujwj1sjj0"  # Replace with your own channel username

# Function to forward messages
def forward_messages(update: Update, context: CallbackContext):
    if update.channel_post:  # If the message is from a public channel
        update.channel_post.forward(chat_id=DESTINATION_CHANNEL)

# Main function to start the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Listen to messages from all public channels
    dp.add_handler(MessageHandler(Filters.chat_type.channel & Filters.all, forward_messages))

    # Start the bot
    updater.start_polling()
    print("Bot is running and forwarding messages from public channels...")
    updater.idle()

if __name__ == "__main__":
    main()
