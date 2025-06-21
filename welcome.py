# welcome.py

import random
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if the user just joined
        if update.chat_member.old_chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED] and \
           update.chat_member.new_chat_member.status == ChatMemberStatus.MEMBER:

            new_user = update.chat_member.new_chat_member.user

            if new_user.is_bot:
                return  # Bot ko welcome nahi karna

            welcome_messages = [
                f"Heyy {new_user.mention_html()} 💖, welcome to the group! 🤗",
                f"Yehhh! {new_user.full_name} aa gaya/aayi 🎉, party to banti hai! 🥳",
                f"Namaste {new_user.mention_html()} 😇, feel at home! 🏡",
                f"Hello hello {new_user.first_name}! 👋 Tere aane se group chamak gaya ✨"
            ]

            await context.bot.send_message(
                chat_id=update.chat_member.chat.id,
                text=random.choice(welcome_messages),
                parse_mode="HTML"
            )

    except Exception as e:
        print(f"[WELCOME ERROR] {e}")
