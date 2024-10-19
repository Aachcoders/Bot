# Import necessary libraries
import logging
from telegram import Update, Bot, ChatInviteLink
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import BadRequest, TelegramError

# Configure logging to help with debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the bot token directly
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Start function that provides a welcome message to the user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to the Group Creation Bot!\n\n"
        "To create a group, use the command: /group @username [optional group name].\n\n"
        "For more information, type /help."
    )

# Help command to explain the bot's functionality
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ To create a group:\n\n"
        "Use the command `/group @username [optional group name]` to create a new group "
        "with another user. If no group name is provided, a default name will be used."
    )

# Group creation logic
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user

    # Check if the command is used in a private chat
    if update.message.chat.type != "private":
        await update.message.reply_text(
            "🚫 Please use this command in a private chat with another user to create a group."
        )
        return

    # Check for a target user (e.g., a mention or reply to a message)
    if len(context.args) < 1:
        await update.message.reply_text(
            "ℹ️ Please provide a target user by replying to their message or mentioning their username."
        )
        return

    target_username = context.args[0]
    group_name = handle_group_name(context.args[1:], user)

    try:
        new_group, invite_link = await create_group_and_invite_link(group_name)
        await add_bot_to_description(new_group)
        await handle_user_invitation(target_username, new_group, invite_link)

        await update.message.reply_text(
            f"✅ Group '{group_name}' created successfully!\n"
            f"An invite link has been sent to {target_username}. They can join using the provided link."
        )

    except TelegramError as e:
        logger.error(f"Error creating group: {str(e)}")
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")

# Helper function to set the group name
def handle_group_name(args, user):
    if args:
        return " ".join(args)
    return f"{user.first_name} <> Target User"

# Function to create a group and invite link
async def create_group_and_invite_link(group_name):
    bot = Bot(token=BOT_TOKEN)
    # Create the new group (supergroup)
    new_group = await bot.create_chat(title=group_name, chat_type="supergroup")

    # Generate the invite link for the group
    invite_link = await new_group.create_invite_link(member_limit=1)
    
    return new_group, invite_link

# Function to set the bot link in the group's description
async def add_bot_to_description(new_group):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.set_chat_description(
            chat_id=new_group.id,
            description="🔗 Link to IntroLink bot: https://t.me/IntroLinkBot"
        )
    except BadRequest as e:
        logger.warning(f"Error setting chat description: {e}")

# Function to handle the invitation of the target user
async def handle_user_invitation(target_username, new_group, invite_link: ChatInviteLink):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=target_username,
            text=f"You've been invited to join the group '{new_group.title}'.\nClick here to join: {invite_link.invite_link}"
        )
    except BadRequest as e:
        logger.error(f"Error sending invite: {e}")
        await bot.send_message(
            chat_id=target_username,
            text="🚫 Could not add you to the group automatically. Please use the invite link."
        )

# Main function to set up the bot and handle commands
def main():
    # Create the bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers for different commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("group", start_group))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot and run it
    application.run_polling()

if __name__ == "__main__":
    main()
    
