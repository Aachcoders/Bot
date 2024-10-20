import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Constants
INTRO_LINK_BOT_URL = "https://t.me/IntroLinkBot"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text("Welcome! Use /group [name] in reply to another user's message to create a new group.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "This bot allows you to create groups easily.\n"
        "Use /group [name] in reply to another user's message to create a new group."
    )

async def process_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the /group command for creating groups."""
    user = update.message.from_user
    message = update.message.reply_to_message

    if not message:
        await update.message.reply_text("Please reply to the user you want to create a group with!")
        return

    target_user = message.from_user
    group_name = " ".join(context.args) if context.args else f"{user.first_name} <> {target_user.first_name}"

    # Mocking group creation (you cannot actually create groups with bots)
    group_id = hash(group_name)  # Mock ID for group creation
    group_link = f"https://t.me/joinchat/{group_id}"  # Mock link

    try:
        # Notify the other user about the new group (mock implementation)
        await context.bot.send_message(
            chat_id=target_user.id,
            text=(f"You have been added to a new group: *{group_name}*. "
                  f"Click here to join: [Join Group]({group_link})\n"
                  f"Also check out IntroLink bot: [IntroLink Bot]({INTRO_LINK_BOT_URL})"),
            parse_mode='MarkdownV2'
        )
        
        await update.message.reply_text(f"Group '{group_name}' created successfully!")
    
    except Exception as e:
        logger.error(f"Error sending message to user {target_user.id}: {e}")
        await update.message.reply_text("Failed to notify the other user.")

def main():
    """Start the bot."""
    # Replace 'YOUR_TOKEN_HERE' with your actual bot token
    application = ApplicationBuilder().token("7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA").build()

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('group', process_group_command))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    main()
