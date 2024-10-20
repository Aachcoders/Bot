import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import BadRequest, TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"User {user.username} has started the bot.")
    await update.message.reply_text("👋 Welcome! Use /group @username to create a group.")

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ *To create a group:*\n"
        "Use the `/group @username [optional group name]` command in someone's DMs. "
        "If no group name is provided, a default one will be used."
    )

# Fetch user by username
async def fetch_user_by_username(username: str):
    bot = Bot(token=BOT_TOKEN)
    try:
        user = await bot.get_chat(username)
        logger.info(f"Fetched user @{username} with ID {user.id}.")
        return user
    except BadRequest as e:
        logger.error(f"Error fetching user @{username}: {str(e)}")
        return None

# Start group command handler
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"User {user.username} wants to create a group.")
    
    # Check if command is being used in DMs
    if update.message.chat.type != "private":
        await update.message.reply_text("🚫 Please use this command in a private chat.")
        return

    # Parse username from the command
    if len(context.args) == 0:
        await update.message.reply_text("❌ Please specify a username. Example: /group @username")
        return

    target_username = context.args[0]
    logger.info(f"Target username: {target_username}")

    # Fetch the target user by username
    target_user = await fetch_user_by_username(target_username)
    if not target_user:
        await update.message.reply_text(f"❌ User @{target_username} not found or hasn’t interacted with the bot.")
        return

    # Define group name (optional)
    group_name = " ".join(context.args[1:]) if len(context.args) > 1 else f"{user.first_name} <> {target_user.first_name}"
    logger.info(f"Group name: {group_name}")

    try:
        # Create the group
        bot = Bot(token=BOT_TOKEN)
        new_group = await bot.create_chat(title=group_name, chat_type="supergroup")
        logger.info(f"Group '{group_name}' created with ID {new_group.id}.")

        # Send invite link to target user
        invite_link = await new_group.create_invite_link()
        await bot.send_message(chat_id=target_user.id, text=f"You've been invited to the group '{group_name}'. Click here to join: {invite_link.invite_link}")
        logger.info(f"Invite link sent to {target_user.username}.")

        await update.message.reply_text(f"✅ Group '{group_name}' created and invite link sent to @{target_username}.")
    except TelegramError as e:
        logger.error(f"Error creating group or sending invite: {str(e)}")
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"An error occurred: {context.error}")
    if update and update.message:
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")

# Main function to set up the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("group", start_group))

    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
