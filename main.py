import logging
from telegram import Update, Bot, ChatInviteLink
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import BadRequest, TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# The Bot Token
BOT_TOKEN = "7803123188:AAFDr0dLsOdDKKEDspegZToOz-mTA8uB3ZA"

# Function: Send welcome message when bot starts
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"User {user.username} has started the bot.")
    
    await update.message.reply_text(
        "👋 Welcome to the Group Creation Bot!\n\n"
        "To create a group, use the command:\n"
        "/group [optional group name] in someone's DMs.\n\n"
        "For help, type /help."
    )

# Function: Send help information
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Help command issued")
    
    await update.message.reply_text(
        "ℹ️ *Instructions to create a group:*\n\n"
        "Use the `/group [optional group name]` command in someone's DMs, "
        "and the bot will create a group with that person.\n"
        "If you don't specify a group name, the group will default to "
        "'[Your Name] <> [Their Name]'."
    )

# Function: Handle the creation of a group chat
async def start_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"User {user.username} initiated a group creation.")

    # Ensure the command is being used in a direct message (DM) chat
    if update.message.chat.type != "private":
        logger.warning(f"User {user.username} attempted to use /group in a non-private chat.")
        await update.message.reply_text("🚫 Please use this command in a direct message with another person.")
        return

    target_user = update.message.chat  # The user the message was sent to
    group_name = handle_group_name(context.args, user, target_user)

    try:
        new_group, invite_link = await create_group_and_invite_link(group_name)
        await add_bot_to_description(new_group)
        await handle_user_invitation(target_user, new_group, invite_link)

        await update.message.reply_text(
            f"✅ Group '{group_name}' created successfully!\n"
            f"An invite link has been sent to {target_user.first_name}."
        )
        logger.info(f"Group '{group_name}' created by {user.username}. Invite link sent to {target_user.first_name}.")
    except TelegramError as e:
        logger.error(f"Error creating group: {str(e)}")
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")

# Helper Function: Handle group name based on input or defaults
def handle_group_name(args, user, target_user):
    if args:
        group_name = " ".join(args)
        logger.info(f"Group name provided by user: {group_name}")
    else:
        group_name = f"{user.first_name} <> {target_user.first_name}"
        logger.info(f"Default group name used: {group_name}")
    
    return group_name

# Function: Create a group chat and generate an invite link
async def create_group_and_invite_link(group_name):
    bot = Bot(token=BOT_TOKEN)
    
    new_group = await bot.create_chat(title=group_name, chat_type="supergroup")
    logger.info(f"Supergroup '{group_name}' created successfully with ID {new_group.id}.")
    
    invite_link = await new_group.create_invite_link(member_limit=2)  # Limit the invite link to 2 users (optional)
    logger.info(f"Invite link generated for group '{group_name}': {invite_link.invite_link}")
    
    return new_group, invite_link

# Function: Add a link to the IntroLink bot in the group description
async def add_bot_to_description(new_group):
    bot = Bot(token=BOT_TOKEN)
    description = "🔗 Link to IntroLink bot: https://t.me/IntroLinkBot"
    
    try:
        await bot.set_chat_description(chat_id=new_group.id, description=description)
        logger.info(f"IntroLink bot link added to group description for {new_group.title}.")
    except BadRequest as e:
        logger.error(f"Failed to set group description: {str(e)}")

# Function: Handle inviting the target user to the new group
async def handle_user_invitation(target_user, new_group, invite_link):
    bot = Bot(token=BOT_TOKEN)
    
    try:
        await bot.send_message(
            chat_id=target_user.id,
            text=f"You've been invited to join the group '{new_group.title}'.\n"
                 f"Click here to join: {invite_link.invite_link}\n"
                 f"Also, check out the IntroLink bot: https://t.me/IntroLinkBot"
        )
        logger.info(f"Invite link sent to {target_user.first_name}.")
    except BadRequest as e:
        logger.error(f"Failed to send invite link to {target_user.first_name}: {str(e)}")
        await bot.send_message(
            chat_id=target_user.id,
            text="🚫 Could not automatically add you to the group. Please use the invite link."
        )

# Function: Gracefully handle errors globally
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"An error occurred: {context.error}")
    if update and update.message:
        await update.message.reply_text("⚠️ An unexpected error occurred. Please try again later.")
    else:
        logger.warning("Update or message is None. Unable to send error response.")

# Main function to initialize the bot and its command handlers
def main():
    logger.info("Initializing the bot...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("group", start_group))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_error_handler(error_handler)
    
    logger.info("Bot is starting... Now polling for updates.")
    application.run_polling(drop_pending_updates=True)  # Added drop_pending_updates for clean start

if __name__ == "__main__":
    main()
    
