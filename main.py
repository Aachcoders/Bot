import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Constants
INTRO_LINK_BOT_URL = "https://t.me/IntroLinkBot"

# Store user data for group creation
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    await update.message.reply_text("Welcome! To create a group, please reply to another user's message with /group.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "This bot allows you to create groups easily.\n"
        "To create a group, reply to another user's message in your DM with /group [name]."
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

    # Store user data for later use
    user_data[user.id] = {
        "target_user_id": target_user.id,
        "group_name": group_name,
        "group_ready": False  # Flag to indicate if the group is ready for creation
    }

    await update.message.reply_text(f"Group '{group_name}' is ready for creation. Please send /done when you're ready.")

async def process_done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the /done command to create the group."""
    user = update.message.from_user

    # Check if the user has initiated a group creation
    if user.id not in user_data:
        await update.message.reply_text("You haven't started a group creation yet! Use /group first.")
        return

    # Retrieve stored data
    target_user_id = user_data[user.id]["target_user_id"]
    group_name = user_data[user.id]["group_name"]

    # Mocking group creation (you cannot actually create groups with bots)
    group_id = hash(group_name)  # Mock ID for group creation
    group_link = f"https://t.me/joinchat/{group_id}"  # Mock link

    try:
        # Notify the other user about the new group (mock implementation)
        await context.bot.send_message(
            chat_id=target_user_id,
            text=(f"You have been added to a new group: *{group_name}*. "
                  f"Click here to join: [Join Group]({group_link})\n"
                  f"Also check out IntroLink bot: [IntroLink Bot]({INTRO_LINK_BOT_URL})"),
            parse_mode='MarkdownV2'
        )
        
        await update.message.reply_text(f"Group '{group_name}' created successfully!")

        # Clean up user data after successful creation
        del user_data[user.id]
    
    except Exception as e:
        logger.error(f"Error sending message to user {target_user_id}: {e}")
        await update.message.reply_text("Failed to notify the other user.")

async def handle_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /group command from the bot's chat."""
    await process_group_command(update, context)

async def handle_done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /done command from the bot's chat."""
    await process_done_command(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages and check for /group command."""
    if update.message.text.startswith('/group'):
        await process_group_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify about it."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    application = ApplicationBuilder().token("7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA").build()
    
    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    
    # Register handlers for /group and /done commands
    application.add_handler(CommandHandler('group', handle_group_command))
    application.add_handler(CommandHandler('done', handle_done_command))
    
    # Register a message handler for DMs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register an error handler
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
