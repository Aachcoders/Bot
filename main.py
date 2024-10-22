import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from telethon import TelegramClient, events
from telethon.tl.types import User as TelegramUser, Chat, Channel
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest
from telethon.errors import (
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    UserPrivacyRestrictedError,
    UserNotMutualContactError,
    UserChannelsTooMuchError,
    UserKickedError,
    UserBannedInChannelError,
    UserBlockedError,
    UserIdInvalidError,
    PeerIdInvalidError,
    FloodWaitError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 20452174
API_HASH = "8269e453f690214f9d9fe71ae0d7df01"
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Simulated database
users_db: Dict[int, 'User'] = {}
groups_db: Dict[str, 'Group'] = {}

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
GROUP_CREATION_COOLDOWN = 300  # seconds
INTROLINK_BOT_LINK = "https://t.me/IntroLinkBot"

class User:
    def __init__(self, user_id: int, username: str, first_name: str, last_name: str):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.settings = UserSettings()
        self.last_group_creation = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    def can_create_group(self) -> bool:
        if self.last_group_creation is None:
            return True
        return (datetime.now() - self.last_group_creation).total_seconds() >= GROUP_CREATION_COOLDOWN

    def update_group_creation_time(self):
        self.last_group_creation = datetime.now()

class UserSettings:
    def __init__(self):
        self.allow_auto_add_to_groups = True
        self.notification_preferences = NotificationPreferences()
        self.privacy_settings = PrivacySettings()

class NotificationPreferences:
    def __init__(self):
        self.group_invites = True
        self.new_messages = True
        self.mentions = True

class PrivacySettings:
    def __init__(self):
        self.show_online_status = True
        self.show_profile_photo = True
        self.allow_calls = True

class Group:
    def __init__(self, group_id: str, name: str, creator_id: int):
        self.group_id = group_id
        self.name = name
        self.creator_id = creator_id
        self.members = set()
        self.created_at = datetime.now()
        self.description = f"Welcome to this group! Check out IntroLink bot: {INTROLINK_BOT_LINK}"
        self.settings = GroupSettings()

    def add_member(self, user_id: int):
        self.members.add(user_id)

    def remove_member(self, user_i : int):
        self.members.discard(user_id)

class GroupSettings:
    def __init__(self):
        self.group_type = "public"
        self.group_title = "IntroLink Group"
        self.group_description = "This is a group created by IntroLink bot"

async def main():
    client = TelegramClient('session', API_ID, API_HASH).start(BOT_TOKEN)
    logger.info("Bot started successfully!")

    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        user_id = event.sender_id
        if user_id not in users_db:
            user = await client.get_entity(event.sender_id)
            users_db[user_id] = User(user_id, user.username, user.first_name, user.last_name)
        await event.respond("Welcome to IntroLink bot! I can help you create groups and manage your connections.")

    @client.on(events.NewMessage(pattern='/create_group'))
    async def create_group(event):
        user_id = event.sender_id
        if user_id not in users_db:
            await event.respond("Please start the bot first by sending /start command.")
            return
        user = users_db[user_id]
        if not user.can_create_group():
            await event.respond("You can create a group only once every 5 minutes.")
            return
        group_name = f"IntroLink Group - {user.full_name}"
        try:
            result = await client(CreateChannelRequest(group_name, "This is a group created by IntroLink bot"))
            group_id = result.chats[0].id
            group = Group(group_id, group_name, user_id)
            groups_db[group_id] = group
            user.update_group_creation_time()
            await event.respond(f"Group created successfully! Group ID: {group_id}")
        except Exception as e:
            await event.respond(f"Failed to create group: {str(e)}")

    @client.on(events.NewMessage(pattern='/invite_to_group'))
    async def invite_to_group(event):
        user_id = event.sender_id
        if user_id not in users_db:
            await event.respond("Please start the bot first by sending /start command.")
            return
        user = users_db[user_id]
        group_id = int(event.text.split()[1])
        if group_id not in groups_db:
            await event.respond("Invalid group ID.")
            return
        group = groups_db[group_id]
        if group.creator_id != user_id:
            await event.respond("You are not the creator of this group.")
            return
        try:
            await client(InviteToChannelRequest(group_id, [event.sender_id]))
            group.add_member(event.sender_id)
            await event.respond("Invitation sent successfully!")
        except Exception as e:
            await event.respond(f"Failed to invite to group: {str(e)}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
