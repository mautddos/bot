from pyrogram import Client

# Fill in your API credentials
API_ID = 22625636  # Your API ID
API_HASH = "f71778a6e1e102f33ccc4aee3b5cc697"  # Your API Hash
BOT_TOKEN = "7685124406:AAHSlQuDOnmhiX5_jU4z1KZA5a3lbIe96aE"  # Your bot token

# Initialize Pyrogram bot
app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def forward_old_messages(source_channel, destination_channel):
    """ Fetch and forward old messages from source to destination """
    async with app:
        async for message in app.get_chat_history(source_channel, limit=1000):  # Adjust limit as needed
            try:
                if message.text or message.caption or message.media:
                    await app.forward_messages(destination_channel, source_channel, message.message_id)
            except Exception as e:
                print(f"⚠️ Error forwarding message {message.message_id}: {e}")

async def main():
    source_channel = "your_source_channel"  # Example: "@my_channel"
    destination_channel = -100123456789  # Destination channel ID

    print("⏳ Forwarding messages. This may take some time...")
    await forward_old_messages(source_channel, destination_channel)
    print("✅ Forwarding completed!")

app.run(main())
