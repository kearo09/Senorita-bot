from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

# Group-wise user warning tracking
user_warnings = {}

async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Kisiko warn karna hai toh uske message pe reply karo na! 😤")
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id

    if chat_id not in user_warnings:
        user_warnings[chat_id] = {}

    if user.id not in user_warnings[chat_id]:
        user_warnings[chat_id][user.id] = 0

    user_warnings[chat_id][user.id] += 1
    warnings = user_warnings[chat_id][user.id]

    if warnings >= 3:
        await context.bot.ban_chat_member(chat_id, user.id)
        await update.message.reply_text(
            f"Bahut ho gaya {user.first_name}! 3 warnings ke baad group se bye bye! 😠"
        )
    else:
        await update.message.reply_text(
            f"{user.first_name}, Warning {warnings}/3! Aur masti ki toh ban karenge! 😡"
        )

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Kisko mute karna hai? Reply karo uske message pe! 😶")
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id

    try:
        mute_duration = int(context.args[0]) if context.args else 5
    except:
        mute_duration = 5

    until_date = datetime.now() + timedelta(minutes=mute_duration)

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        ),
        until_date=until_date
    )

    await update.message.reply_text(
        f"{user.first_name} ko {mute_duration} minutes ke liye mute kar diya gaya 😷"
    )

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Ban karna hai? Reply toh karo bhai uske message pe! 😑")
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.message.chat_id

    await context.bot.ban_chat_member(chat_id, user.id)
    await update.message.reply_text(
        f"{user.first_name} ko group se ban kar diya gaya! 🚫👋"
    )
