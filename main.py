import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from telethon import TelegramClient, events
from telethon.tl.types import User as TelegramUser, Chat, Channel
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
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

# Bot configuration
API_ID = 20452174
API_HASH = "8269e453f690214f9d9fe71ae0d7df01"
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Simulated database
users_db: Dict[int, 'User'] = {}
groups_db: Dict[str, 'Group'] = {}

# Constants
INTROLINK_BOT_LINK = "https://t.me/IntroLinkBot"

class User:
    def __init__(self, user_id: int, username: str, first_name: str, last_name: str):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.settings = UserSettings()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

class UserSettings:
    def __init__(self):
        self.allow_auto_add_to_groups = True

class Group:
    def __init__(self, group_id: str, name: str, creator_id: int):
        self.group_id = group_id
        self.name = name
        self.creator_id = creator_id
        self.members = set()
        self.created_at = datetime.now()
        self.description = f"Welcome to this group! Check out IntroLink bot: {INTROLINK_BOT_LINK}"

    def add_member(self, user_id: int):
        self.members.add(user_id)

async def main():
    client = TelegramClient('session', API_ID, API_HASH).start(BOT_TOKEN)
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        user_id = event.sender_id
        if user_id not in users_db:
            user = await client.get_entity(event.sender_id)
            users_db[user_id] = User(user_id, user.username, user.first_name, user.last_name)
        await event.respond("Welcome to IntroLink bot! I can help you create groups and manage your connections.")

    @client.on(events.NewMessage(pattern='/group'))
    async def create_group(event):
        if not event.is_private:
            await event.respond("This command can only be used in direct messages.")
            return

        sender = await event.get_sender()
        chat = await event.get_chat()

        if sender.id == chat.id:
            await event.respond("This command should be used in a direct message with another user.")
            return

        user = users_db.get(sender.id) or User(sender.id, sender.username, sender.first_name, sender.last_name)
        other_user = await client.get_entity(chat.id)

        # Parse group name
        group_name = ' '.join(event.text .split()[1:])
        if not group_name:
            group_name = f"{user.full_name} <> {other_user.first_name} {other_user.last_name}"

        try:
            result = await client(CreateChatRequest([other_user.id], group_name))
            group_id = result.chats[0].id
            group = Group(group_id, group_name, sender.id)
            groups_db[group_id] = group
            group.add_member(sender.id)
            group.add_member(other_user.id)

            # Add users to the group
            await client(AddChatUserRequest(group_id, other_user.id, 0))
            await client(AddChatUserRequest(group_id, sender.id, 0))

            # Send invitation to the other user
            await client.send_message(other_user.id, f"Join the group: {group_name} - https://t.me/IntroLinkBot")

            await event.respond(f"Group created successfully! Group ID: {group_id}")
        except Exception as e:
            await event.respond(f"Failed to create group: {str(e)}")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
