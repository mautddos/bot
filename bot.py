from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# --- BOT CONFIGURATION ---
BOT_TOKEN = "7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE"
DESTINATION_CHANNEL = "@aaannndndjdhwuwhwvsw92iujwj1sjj0"  # Replace with your own channel username

# Function to forward messages
async def forward_messages(update: Update, context: CallbackContext):
    if update.channel_post:  # If the message is from a public channel
        await update.channel_post.forward(chat_id=DESTINATION_CHANNEL)

# Main function to start the bot
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Listen to messages from all public channels
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.ALL, forward_messages))

    print("Bot is running and forwarding messages from public channels...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
