# welcome.py
import random
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("✅ Member update detected!")  # Debug print

        if update.chat_member.old_chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED] and \
           update.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:

            user = update.chat_member.new_chat_member.user
            if user.is_bot:
                return

            welcome_msgs = [
                f"Heyy {user.mention_html()} 💖, welcome to the group! 🤗",
                f"Namaste {user.first_name} 😇, feel at home! 🏡",
                f"Yehhh! {user.full_name} aa gaya/aayi 🎉, party to banti hai! 🥳"
            ]

            await context.bot.send_message(
                chat_id=update.chat_member.chat.id,
                text=random.choice(welcome_msgs),
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"[WELCOME ERROR] {e}")

