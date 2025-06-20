from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
import json
import os

# 👑 Owner IDs (they can use commands even if not admin)
OWNER_IDS = [7638769372, 7856649680, 6523934792]

# Warns data stored in JSON file
WARN_FILE = "warns.json"

# Load warn data
if os.path.exists(WARN_FILE):
    with open(WARN_FILE, "r") as f:
        warn_data = json.load(f)
else:
    warn_data = {}

# ✅ Check if user is admin or owner
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id in OWNER_IDS:
        return True

    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ['administrator', 'creator']

# ✅ Check if target is admin
async def is_target_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    try:
        member = await context.bot.get_chat_member(chat_id, target_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

# ⚠️ WARN command
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = str(user.id)
    chat_id = str(update.effective_chat.id)

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin ko warn nahi kar sakte boss 😅")
        return

    if int(user_id) in OWNER_IDS:
        await update.message.reply_text("😇 Sorry, me apne owner ko warn nahi kar sakti 😒")
        return

    if chat_id not in warn_data:
        warn_data[chat_id] = {}
    if user_id not in warn_data[chat_id]:
        warn_data[chat_id][user_id] = 0

    warn_data[chat_id][user_id] += 1
    warns = warn_data[chat_id][user_id]

    with open(WARN_FILE, "w") as f:
        json.dump(warn_data, f)

    if warns >= 3:
        await context.bot.ban_chat_member(chat_id=int(chat_id), user_id=int(user_id))
        await update.message.reply_text(f"🚫 {user.first_name} ko 3 warnings ke baad ban kar diya gaya hai.")
        del warn_data[chat_id][user_id]
        with open(WARN_FILE, "w") as f:
            json.dump(warn_data, f)
    else:
        await update.message.reply_text(f"⚠️ {user.first_name} ko warning di gayi hai. ({warns}/3)")

# 🔇 MUTE
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin ko mute nahi kar sakte boss 😅")
        return
    if user_id in OWNER_IDS:
        await update.message.reply_text("😇 Sorry, me apne owner ko mute nahi kar sakti 😒")
        return

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("🔇 User ko permanently mute kar diya gaya hai.")

# 🚫 BAN
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin ko ban nahi kar sakte boss 😅")
        return
    if user_id in OWNER_IDS:
        await update.message.reply_text("😇 Sorry, me apne owner ko ban nahi kar sakti 😒")
        return

    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    await update.message.reply_text("🚫 User ko group se ban kar diya gaya hai.")

# ✅ UNWARN
async def unwarn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = str(user.id)
    chat_id = str(update.effective_chat.id)

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin h wo, Dekh to lia karo 😒")
        return
    if int(user_id) in OWNER_IDS:
        await update.message.reply_text("😇 Mera owner h wo, warnings nahi hata sakti 😒")
        return

    if chat_id in warn_data and user_id in warn_data[chat_id]:
        del warn_data[chat_id][user_id]
        with open(WARN_FILE, "w") as f:
            json.dump(warn_data, f)
        await update.message.reply_text("✅ User ke warnings reset kar diye gaye hain.")
    else:
        await update.message.reply_text("❌ Is user ke paas koi warning nahi thi.")

# 🔓 UNMUTE
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin h wo, Dekh to lia karo 😒")
        return
    if user_id in OWNER_IDS:
        await update.message.reply_text("😇 Mera owner h wo, unmute ka kya hi karungi 😅")
        return

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("🔓 User ko unmute kar diya gaya hai.")

# 🙌 UNBAN
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ Ye command sirf admins ke liye hai!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Kisi user ko reply karke command do.")
        return

    user = update.message.reply_to_message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if await is_target_admin(update, context):
        await update.message.reply_text("❌ Admin h wo, Dekh to lia karo 😒")
        return
    if user_id in OWNER_IDS:
        await update.message.reply_text("😇 Apne owner ko unban nahi karti 😌")
        return

    await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
    await update.message.reply_text("🙌 User ko group se unban kar diya gaya hai.")
