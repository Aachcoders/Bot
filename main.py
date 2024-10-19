# Importing necessary libraries
from telegram import Update, Bot, ChatInviteLink, User
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
import os

# Define the bot token directly (make sure to keep this secure in production)
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"  # Your bot token

# Function: Starts the group creation process
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the command is used in a private chat with another individual
    if update.message.chat.type != "private":
        await update.message.reply_text("Please use this command in a private chat.")
        return
    
    # Get user and target information
    user = update.message.from_user
    target = update.message.chat
    
    # Handle the group name based on user input or default behavior
    group_name = handle_group_name(context.args, user, target)

    # Create the group chat and invite link
    new_group, invite_link = await create_group_and_invite_link(group_name)

    # Add the IntroLink bot to the description
    await add_bot_to_description(new_group)

    # Send the invite link to the other user and add them automatically if allowed
    await handle_user_invitation(target, new_group, invite_link)

    # Reply to the command sender
    await update.message.reply_text(f"Group '{group_name}' created. Invite link sent to the target user.")

# Helper function: Handles the group name
def handle_group_name(args, user: User, target: User):
    """
    Handles the group name based on user input or defaults to the format:
    [user’s name] <> [other person's name]
    """
    if args:
        group_name = " ".join(args)
    else:
        group_name = f"{user.first_name} <> {target.first_name}"
    return group_name

# Helper function: Creates the group and generates an invite link
async def create_group_and_invite_link(group_name):
    """
    Creates a new supergroup and generates an invite link for the group.
    """
    # Create the new group chat
    new_group = await bot.create_chat(title=group_name, chat_type="supergroup")

    # Create an invite link for the group
    invite_link = await new_group.create_invite_link(member_limit=1, creates_join_request=False)
    
    return new_group, invite_link

# Helper function: Adds the IntroLink bot to the group's description
async def add_bot_to_description(new_group):
    """
    Adds a link to the IntroLink bot in the group's description field.
    """
    await bot.set_chat_description(
        chat_id=new_group.id,
        description="Link to IntroLink bot: https://t.me/IntroLinkBot"
    )

# Helper function: Handles user invitation to the group
async def handle_user_invitation(target, new_group, invite_link: ChatInviteLink):
    """
    Sends an invite link to the other user and adds them automatically
    if their settings allow it.
    """
    # Send the invite link to the other user
    await bot.send_message(
        chat_id=target.id,
        text=f"You've been invited to join the group. Click here to join: {invite_link.invite_link}"
    )

    # Automatically add the target user if allowed by their settings
    if target.can_be_invited:
        await bot.add_chat_members(chat_id=new_group.id, user_ids=[target.id])

# Function: Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /start command. Provides basic instructions.
    """
    await update.message.reply_text("Welcome to the group creation bot! Use /group to create a new group.")

# Function: Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /help command. Explains how the bot works.
    """
    await update.message.reply_text(
        "Use the command /group [optional group name] to create a group with "
        "another user. If no name is provided, the group will be named as "
        "[Your Name] <> [Other User's Name]."
    )

# Function to start the bot and add command handlers
def main():
    # Create an Application instance
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers for the commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("group", start_group))
    application.add_handler(CommandHandler("help", help_command))

    # Start polling updates
    application.run_polling()

# Call the main function if running as the main script
if __name__ == '__main__':
    main()
