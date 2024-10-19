# Import necessary libraries
from telegram import Update, Bot, ChatInviteLink
from telegram.ext import CommandHandler, ApplicationBuilder, ContextTypes
from telegram.error import BadRequest, TelegramError
from telegram.helpers import mention_html
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the bot token directly (keep this secure in production)
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"  # Your bot token

# Function: Starts the group creation process
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # Ensure the command is used in a private chat
    if update.message.chat.type != "private":
        await update.message.reply_text(
            "🚫 Please use this command in a private chat with another user to create a group."
        )
        return

    # Check if there is a target user (reply to a message or mention another user)
    if len(context.args) < 1:
        await update.message.reply_text(
            "ℹ️ To create a group, please provide a target user by replying to their message "
            "or by mentioning them in the command like /group @username."
        )
        return

    # Get the target user's ID and handle group name
    target_user_id = context.args[0]  # assuming @username format
    group_name = handle_group_name(context.args[1:], user)

    try:
        # Create the group and invite link
        new_group, invite_link = await create_group_and_invite_link(group_name)

        # Add the IntroLink bot to the group description
        await add_bot_to_description(new_group)

        # Send invite link to the target user
        await handle_user_invitation(target_user_id, new_group, invite_link)

        # Reply to the command sender
        await update.message.reply_text(
            f"✅ Group '{group_name}' created successfully! 🎉\n"
            f"An invite link has been sent to the target user. They can join using the link provided."
        )

    except TelegramError as e:
        logger.error(f"Error creating group: {str(e)}")
        await update.message.reply_text(
            f"❌ An error occurred while creating the group: {str(e)}"
        )

# Helper function: Handles the group name
def handle_group_name(args, user):
    """
    Returns the group name based on user input or defaults to the format:
    [user’s name] <> [target user’s name]
    """
    if args:
        group_name = " ".join(args)
    else:
        group_name = f"{user.first_name} <> Target User"
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
    try:
        await bot.set_chat_description(
            chat_id=new_group.id,
            description="🔗 Link to IntroLink bot: https://t.me/IntroLinkBot"
        )
    except BadRequest as e:
        logger.warning(f"Error setting chat description: {e}")

# Helper function: Sends an invite link to the target user and adds them to the group
async def handle_user_invitation(target_user_id, new_group, invite_link: ChatInviteLink):
    """
    Sends an invite link to the target user and adds them automatically
    if their settings allow it.
    """
    try:
        # Send the invite link to the target user
        await bot.send_message(
            chat_id=target_user_id,
            text=f"You've been invited to join the group '{new_group.title}'. Click here to join: {invite_link.invite_link}"
        )

        # Automatically add the target user if allowed by their settings
        await bot.add_chat_members(chat_id=new_group.id, user_ids=[target_user_id])

    except BadRequest as e:
        logger.error(f"Error sending message or adding user: {e}")
        await bot.send_message(
            chat_id=target_user_id,
            text="🚫 I couldn't add you to the group automatically. Please join using the invite link."
        )

# Function: Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /start command. Provides basic instructions.
    """
    await update.message.reply_text(
        "👋 Welcome to the Group Creation Bot!\n\n"
        "To create a new group chat with another user, use the command:\n"
        "/group @username [optional group name]\n\n"
        "Replace '@username' with the target user's username and optionally provide a group name.\n"
        "Example: /group @john_doe My Group\n\n"
        "Use /help for more information."
    )

# Function: Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /help command. Explains how the bot works.
    """
    await update.message.reply_text(
        "ℹ️ **Help**\n\n"
        "Use the command `/group @username [optional group name]` to create a group with "
        "another user.\n"
        "If no name is provided, the group will be named as '[Your Name] <> [Other User's Name]'.\n\n"
        "Make sure to mention the username of the person you want to group with.\n"
        "If you encounter any issues, feel free to reach out to the bot owner!"
    )

# Function: List available commands
async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Provides a list of available commands for the user.
    """
    commands = [
        "/start - Welcome message and instructions.",
        "/group @username [optional group name] - Create a new group chat with another user.",
        "/help - Get help on how to use this bot.",
        "/commands - List all available commands."
    ]
    await update.message.reply_text("\n".join(commands))

# Function: Provide feedback to the user
async def user_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Collects feedback from the user regarding the bot.
    """
    feedback_message = "Please provide your feedback about the bot:"
    await update.message.reply_text(feedback_message)

    # Set up a conversation state or direct message user for feedback (not implemented)
    # This would typically involve state management to handle user responses

# Function: Main bot setup and command handlers
def main():
    # Create an Application instance
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers for the bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("group", start_group))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("commands", commands_list))
    application.add_handler(CommandHandler("feedback", user_feedback))

    # Start polling updates
    application.run_polling()

# Call the main function if running as the main script
if __name__ == '__main__':
    main()
    
