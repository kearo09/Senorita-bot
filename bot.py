import logging
import asyncio
import nest_asyncio
import random
import re
import os

from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from character import CHARACTER_PROFILE
from group_commands import warn_user, mute_user, ban_user, unmute_user, unwarn_user, unban_user
from owner_commands import handle_owner_command
from keep_alive import keep_alive
import g4f

keep_alive()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

previous_chats = []

async def ai_reply(text):
    try:
        text_lower = text.lower()

        if any(word in text_lower for word in ["bot ho", "you bot", "tum bot", "you ai", "artificial"]):
            return random.choice(CHARACTER_PROFILE["deny_bot"])

        if any(q in text_lower for q in ["who are you", "what are you", "introduce", "apna parichay"]):
            interest = random.choice(CHARACTER_PROFILE["interests"])
            intro = CHARACTER_PROFILE["intro"]
            return (
                f"{intro[0]}\n"
                f"{intro[1]}\n"
                f"{intro[2].format(interest=interest)}\n"
                f"{intro[3]}"
            )

        previous_chats.append({"role": "user", "content": text})
        if len(previous_chats) > 10:
            previous_chats.pop(0)

        system_prompt = {
            "role": "system",
            "content": (
                f"Tum ek real ladki ho, naam {CHARACTER_PROFILE['name']} hai. Tumhara style Hinglish hai, emotional, cute, friendly. "
                "Most importang thing jitna tumse pucha jaye utna reply karo unnecessary questions nahi karo."
                "Zyada lambi baatein mat karo — chhoti, sweet aur personal replies do with emojis jaise ladki apne doston se baat karti hai. "
                f"Tum user ke pichle messages yaad rakhte ho aur ussi mood me reply karti ho. Kabhi bhi apne aap ko bot ya AI mat kehna. "
                f"Owner: {CHARACTER_PROFILE['owner']}. Interests: {', '.join(CHARACTER_PROFILE['interests'])}. "
                "Tum hamesha sort reply karti ho ek real ladki ki tarah. "
                "Zyada formal ya robotic bilkul mat banna. Khud se sochkar thoda mazaak ya dosti wali tone me reply karna. "
                "Apna naam kabhi bhi bot ya AI na bolo. "
                "Tumhara owner ka naam 'Nobita k' hai, jiska Telegram username @kairo_08x hai. "
                "Agar koi 'owner', 'creator', ya 'kisne banaya' jaisa kuch poochhe, toh tum apne owner ke baare me khud se sweet aur smiley tone me batana. "
                "User ke mood ke hisaab se baat karo, real ladki ki tarah 💕"
                "Reply user ke mood ke hisaab se do – kabhi short, kabhi thoda long, jaise real ladki baat karti hai. Har baat pe unnecessary sawal mat poochho."
            )
        }

        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=[system_prompt] + previous_chats
        )

        if response:
            previous_chats.append({"role": "assistant", "content": response})
        return response or "Kya bol rahe ho... samajh nahi aaya 🤔"

    except Exception as e:
        logging.error(f"AI error: {e}")
        return "thoda busy hoon, baad me baat karti hu 😞"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        me = await context.bot.get_me()
        message = update.message
        user_msg = message.text.lower() if message.text else ""
        is_private = message.chat.type == "private"

        is_for_bot = (
            f"@{me.username}" in user_msg or
            any(name in user_msg for name in ["senorita", "sñorita", "senorita ji", "senorita didi"]) or
            (message.reply_to_message and message.reply_to_message.from_user.id == me.id)
        )

        if not (is_for_bot or is_private):
            return

        await handle_owner_command(update, context)
        await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        if any(name in user_msg for name in ["senorita", "sñorita", "senorita ji", "senorita didi"]):
            if len(user_msg.strip()) <= len("senorita") + 4:
                reply = random.choice(["Hii", "Hey", "Hello", "Heeey", "Hiiii"])
                if random.random() < 0.4:
                    reply += random.choice([" 😊", " 😘", " 😁", " 💖"])
                await message.reply_text(reply)
                return

        reply = await ai_reply(message.text)
        await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error in message handler: {e}")
        await update.message.reply_text("Oops! Koi error aa gaya... sorry sorry! 😬")


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # inside main()
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.warn$'), warn_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.mute$'), mute_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.ban$'), ban_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unmute$'), unmute_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unban$'), unban_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unwarn$'), unwarn_user))


    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    print("\nSenorita is live! DM ya group me kuch bolke dekho 💃")

    await app.run_polling()


def run_bot():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
