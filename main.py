import logging
from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 20452174
API_HASH = "8269e453f690214f9d9fe71ae0d7df01"
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Create the client
client = TelegramClient('bot_session', API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
    await event.reply("Welcome to IntroLink bot! Use /group to create a new group.")

@client.on(events.NewMessage(pattern='/group'))
async def group_command(event):
    if not event.is_private:
        await event.reply("This command can only be used in direct messages.")
        return

    sender = await event.get_sender()
    chat = await event.get_chat()

    if sender.id == chat.id:
        await event.reply("Please forward a message from the user you want to create a group with, then use /group.")
        return

    try:
        group_name = f"Group with {sender.first_name} and {chat.first_name}"
        result = await client(CreateChatRequest(users=[chat.id], title=group_name))
        chat_id = result.chats[0].id
        await event.reply(f"Group '{group_name}' created successfully! Group ID: {chat_id}")
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        await event.reply(f"Error creating group: {str(e)}")

async def main():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("Bot started successfully!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
