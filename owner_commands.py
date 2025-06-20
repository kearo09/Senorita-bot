from telegram import Update
from telegram.ext import ContextTypes

OWNER_ID = 7638769372  # <-- Apna Telegram ID

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
