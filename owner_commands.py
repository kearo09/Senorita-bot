import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

# 👑 Owner IDs (they can warn even without admin rights)
OWNER_IDS = [7638769372, 7856649680]  # Replace with real Telegram IDs

# 🚨 Warn data: chat-wise user-wise warning counts
warn_data = {}

# 💬 Cute Senorita replies
WARN_REPLIES = [
    "Jaisa aap kahe, owner 😇",
    "Jesi aapki ichha, Nobi 😊",
    "As your wish, My sweet Owner ✨",
    "Done ho gaya, sirf aap ke liye 💅",
    "Theek hai ji, aapka hukum sar aankhon pe 😍",
    "Command received, executing with love 💖",
    "Aapne kaha aur Senorita ne kar diya 😎",
    "Chali gayi warning, aapka farmaan tha 😈",
    "Sorry bolo owner ko warning remove karne ke lie",
    "Jaise aap chaho Nobi 🙃",
    "Kar diya owner, ab aap chain se baat kariye 😌",
    "Done! Nobi, apne jo kaha tha 😉",
    "Jesa aap kahe Nobi😉",
    "😉Jesa aap kahe Nobi",
    "Warning de di, but sirf aapke kehne pe 💌",
    "warn kar diya, aapki marzi 😇",
    "Ab ye chup rahega… kyuki aapne kaha 😶",
    "sirf aapke liye 😘",
    "Banned! Jaise mere handsome owner ne bola 🥰"
]
# 💥 Admins ko warn nahi kar sakti reply
ADMIN_WARN_BLOCK = "Sorry owner 😇 admin ko warn nahi kar sakti..."

# ❌ Agar bot ke paas rights nahi hon
NO_POWER_REPLY = "Sorry owner 😔 mere paas warn dene ka power nahi hai..."

# ✅ Warn Handler Function
async def owner_warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    sender = message.from_user
    chat_id = update.effective_chat.id

    if not message.reply_to_message:
        await message.reply_text("Owner ji, please reply to the user's message you want to warn 😇")
        return

    target_user = message.reply_to_message.from_user
    target_id = target_user.id

    # Bot's own permissions
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)

    # Check if target is admin
    target_status = (await context.bot.get_chat_member(chat_id, target_id)).status
    if target_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply_text(ADMIN_WARN_BLOCK)
        return

    # If sender is not bot owner, must be admin
    sender_is_owner = sender.id in OWNER_IDS
    sender_status = (await context.bot.get_chat_member(chat_id, sender.id)).status
    sender_is_admin = sender_status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

    if not sender_is_owner and not sender_is_admin:
        return  # Ignore non-owner, non-admins

    # If sender is not owner, bot must have rights
    if not sender_is_owner and not bot_member.can_restrict_members:
        await message.reply_text(NO_POWER_REPLY)
        return

    # Add warning
    if chat_id not in warn_data:
        warn_data[chat_id] = {}
    if target_id not in warn_data[chat_id]:
        warn_data[chat_id][target_id] = 0

    warn_data[chat_id][target_id] += 1
    count = warn_data[chat_id][target_id]

    reply_text = random.choice(WARN_REPLIES)
    await message.reply_text(f"{reply_text}\n⚠️ Total warnings: {count}")



async def handle_owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return  # Not owner, ignore

    user_msg = update.message.text.lower()

    if any(word in user_msg for word in ["say", "bol", "kehdo", "message", "keh de", "dedo"]):
        if "to" in user_msg:
            parts = user_msg.split("to")
            if len(parts) >= 2:
                message = parts[0].replace("senorita", "").replace("say", "").replace("bol", "").replace("kehdo", "").strip()
                receiver = parts[1].strip().capitalize()

                if message and receiver:
                    bot_reply = (
                        f"{receiver}, {message} 💌\n"
                    )
                    await update.message.reply_text(bot_reply)
