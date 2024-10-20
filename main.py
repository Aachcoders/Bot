import logging
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Constants
INTRO_LINK_BOT_URL = "https://t.me/IntroLinkBot"

# Helper Functions

def create_group_chat(group_name):
    """Function to create a group chat with the specified name."""
    try:
        # Placeholder logic for creating a group chat
        new_group_id = hash(group_name)  # Mock ID for group creation
        return new_group_id
    except Exception as e:
        logger.error(f"Error creating group chat: {e}")
        return None

def notify_user(bot, target_user_id, group_name, group_link):
    """Function to notify another user about the new group."""
    try:
        bot.send_message(
            chat_id=target_user_id,
            text=(f"You have been added to a new group: *{group_name}*. "
                  f"Click here to join: [Join Group]({group_link})\n"
                  f"Also check out IntroLink bot: [IntroLink Bot]({INTRO_LINK_BOT_URL})"),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return True
    except Exception as e:
        logger.error(f"Error notifying user: {e}")
        return False

def process_group_command(update: Update, context: CallbackContext) -> None:
    """Process the /group command for creating groups."""
    user = update.message.from_user
    message = update.message.reply_to_message

    if not message:
        update.message.reply_text("Please reply to the user you want to create a group with!")
        return

    target_user = message.from_user
    group_name = " ".join(context.args) if context.args else f"{user.first_name} <> {target_user.first_name}"
    
    # Create the group chat and notify the target user
    group_id = create_group_chat(group_name)

    if group_id is not None:
        group_link = f"https://t.me/joinchat/{group_id}"  # Mock link
        if notify_user(context.bot, target_user.id, group_name, group_link):
            update.message.reply_text(f"Group '{group_name}' created successfully!")
        else:
            update.message.reply_text("Failed to notify the other user.")
    else:
        update.message.reply_text("Failed to create the group.")

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("Welcome! Use /group [name] to create a new group.")

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "This bot allows you to create groups easily.\n"
        "Use /group [name] in reply to another user's message to create a new group."
    )

def main():
    """Start the bot."""
    updater = Updater("7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA")

    # Register command handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CommandHandler('group', process_group_command))

    # Start polling for updates
    updater.start_polling()

    # Run until you send a signal to stop (Ctrl+C)
    updater.idle()

if __name__ == '__main__':
    main()
