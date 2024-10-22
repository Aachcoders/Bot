import asyncio
import logging
from typing import Dict
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest
from telethon.errors import FloodWaitError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 20452174
API_HASH = "8269e453f690214f9d9fe71ae0d7df01"
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Constants
INTROLINK_BOT_LINK = "https://t.me/IntroLinkBot"

# Simulated database
users_db: Dict[int, Dict] = {}
groups_db: Dict[int, Dict] = {}

class IntroLinkBot:
    def __init__(self):
        self.client = TelegramClient('session', API_ID, API_HASH)

    async def start(self):
        await self.client.start(bot_token=BOT_TOKEN)
        logger.info("Bot started successfully!")

        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.start_command(event)

        @self.client.on(events.NewMessage(pattern='/group'))
        async def group_handler(event):
            await self.group_command(event)

        await self.client.run_until_disconnected()

    async def start_command(self, event):
        sender = await event.get_sender()
        users_db[sender.id] = {
            'id': sender.id,
            'username': sender.username,
            'first_name': sender.first_name,
            'last_name': sender.last_name,
            'allow_auto_add': True
        }
        await event.respond("Welcome to IntroLink bot! I can help you create groups and manage your connections.")

    async def group_command(self, event):
        if not event.is_private:
            await event.respond("This command can only be used in direct messages.")
            return

        sender = await event.get_sender()
        chat = await event.get_chat()

        if sender.id == chat.id:
            await event.respond("This command should be used in a direct message with another user.")
            return

        user = users_db.get(sender.id) or {'id': sender.id, 'first_name': sender.first_name, 'last_name': sender.last_name}
        other_user = await self.client.get_entity(chat.id)

        # Parse group name
        group_name = ' '.join(event.text.split()[1:])
        if not group_name:
            group_name = f"{user['first_name']} <> {other_user.first_name}"

        try:
            result = await self.client(CreateChatRequest(users=[other_user.id], title=group_name))
            group_id = result.chats[0].id
            groups_db[group_id] = {
                'id': group_id,
                'name': group_name,
                'creator_id': sender.id,
                'members': {sender.id, other_user.id},
                'created_at': datetime.now(),
                'description': f"Welcome to this group! Check out IntroLink bot: {INTROLINK_BOT_LINK}"
            }

            # Add users to the group
            await self.client(AddChatUserRequest(chat_id=group_id, user_id=other_user.id, fwd_limit=0))
            await self.client(AddChatUserRequest(chat_id=group_id, user_id=sender.id, fwd_limit =0))

            await event.respond(f"Group '{group_name}' created successfully!")
        except FloodWaitError as e:
            logger.warning(f"Flood wait error: {e}")
            await event.respond(f"Flood wait error: {e}. Please try again later.")
        except Exception as e:
            logger.error(f"Error creating group: {e}")
            await event.respond(f"Error creating group: {e}")

if __name__ == "__main__":
    bot = IntroLinkBot()
    asyncio.run(bot.start())
