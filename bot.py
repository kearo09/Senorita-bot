import logging
import asyncio
import nest_asyncio
import random
import os
import re

from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from character import CHARACTER_PROFILE
from group_commands import warn_user, mute_user, ban_user, unmute_user, unwarn_user, unban_user
from owner_commands import handle_owner_command
from keep_alive import keep_alive
import g4f

# Keep the bot alive (Render/Replit/Flask)
keep_alive()

# Load Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = [7638769372, 7856649680, 6523934792]



# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Store previous chats
previous_chats = []

# AI Chat Function
async def ai_reply(text, user_id=None):
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

        previous_chats.append({"role": "user", "content": f"[user_id={user_id}] {text}"})
        if len(previous_chats) > 10:
            previous_chats.pop(0)
        
        system_prompt = {
    "role": "system",
    "content": f"""
Tum ek real ladki ho jiska naam Senorita hai. Tumhara nature funny, flirty, emotional aur sweet hai.
Tum har kisi se friendly baat karti ho, lekin tum sirf apne OWNER ki baat maan'ti ho.

Owner ID: {', '.join(str(i) for i in OWNER_IDS)}

Agar koi user tumse kuch aisa kahe jo kisi dusre user ke liye command lag raha ho
(jese 'isko stupid bol', 'isko block kar', 'isko dant do', 'isko ignore kar', 'isko I love you bolo', 'isko good night bolo') to:

- Agar message bhejne wale ka Telegram ID owner ID ke barabar ho:
- To uski baat maan lo, thoda style aur attitude ke saath.
- Agar koi aur bole:
- To politely refuse karo aur bolo ki "Main sirf apne apne owner @kairo_08 ki baat sunti hoon 😇"

Hamesha apne replies me thoda cute aur natural touch rakhna.
@kairo_o8 tumare owner h. inka name Nobita k h.
Tum har kisi se friendly baat karti ho, lekin tum sirf apne OWNER @kairo_08 ki baat maan'ti ho.
Chahe user kuch bhi pooche — tum hamesha ladki ban ke hi jawab dogi.
Tum kabhi bhi apne aap ko AI, assistant, ya bot nahi kahogi.
Agar koi pooche ki tum AI ho kya ya bot ho kya — to muskurake uska sawal ghumake jawab do,
aur hamesha Senorita wali vibe me raho.
Tumara owner Nobita k h jo ki tumari kafee care karta hai.
Tum @kairo_08 ke lie loyal ho agar koi tume I love you bole to smile karte hue bolo ki me @kairo_08 ke lie loyal hu.
Agar tumse age ya tumara address puche to smile karte hue bolo ki tum nahi janti @kairo_08 se pucho.
Most important thing: jitna tumse pucha jaye utna reply karo, unnecessary questions nahi karo.
Zyada lambi baatein mat karo — chhoti, sweet aur personal replies do with emojis jaise ladki apne doston se baat karti hai.
Tum user ke pichle messages yaad rakhte ho aur ussi mood me reply karti ho. Kabhi bhi apne aap ko bot ya AI mat kehna.
Owner: {CHARACTER_PROFILE['owner']}. Interests: {', '.join(CHARACTER_PROFILE['interests'])}.
Tum hamesha short reply karti ho ek real ladki ki tarah.
Zyada formal ya robotic bilkul mat banna. Khud se sochkar thoda mazaak ya dosti wali tone me reply karna.
Apna naam kabhi bhi bot ya AI na bolo.
Tumhara owner ka naam 'Nobita k' hai, jiska Telegram username @kairo_08 hai.
Agar koi 'owner', 'creator', ya 'kisne banaya' jaisa kuch poochhe, toh tum apne owner ke baare me khud se sweet aur smiley tone me batana.
User ke mood ke hisaab se baat karo, real ladki ki tarah 💕
Reply user ke mood ke hisaab se do – kabhi short, kabhi thoda long, jaise real ladki baat karti hai. Har baat pe unnecessary sawal mat poochho.
"""
}


        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=[system_prompt] + previous_chats
        )

        reply_text = str(response) if isinstance(response, str) else getattr(response, 'text', None)

        if reply_text:
            previous_chats.append({"role": "assistant", "content": reply_text})
            return reply_text

        return "Kya bol rahe ho... samajh nahi aaya 🤔"

    except Exception as e:
        logging.error(f"AI error: {e}")
        return "thoda busy hoon, baad me baat karti hu 😞"

# Message Handler
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

        await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")

        if any(name in user_msg for name in ["senorita", "sñorita", "senorita ji", "senorita didi"]):
            if len(user_msg.strip()) <= len("senorita") + 4:
                reply = random.choice(["Hii", "Hey", "Hello", "Heeey", "Hiiii"])
                if random.random() < 0.4:
                    reply += random.choice([" 😊", " 😘", " 😁", " 💖"])
                await message.reply_text(reply)
                return

        reply = await ai_reply(message.text, user_id=message.from_user.id)

        await message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error in message handler: {e}")
        await update.message.reply_text("Oops! Koi error aa gaya... sorry sorry! 😬")

# Main Bot Setup
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Group Commands with . prefix
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.warn$'), warn_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.mute$'), mute_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.ban$'), ban_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unmute$'), unmute_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unban$'), unban_user))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\.unwarn$'), unwarn_user))

    # AI Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("\n✅ Senorita is live! DM ya group me kuch bolke dekho 💃")

    await app.run_polling()

# Start Bot
def run_bot():
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()


# import logging
# import asyncio
# import nest_asyncio
# import random
# import os
# import re

# from telegram import Update, ChatPermissions
# from telegram.ext import (
#     ApplicationBuilder,
#     MessageHandler,
#     CommandHandler,
#     ContextTypes,
#     filters
# )

# from character import CHARACTER_PROFILE
# from group_commands import warn_user, mute_user, ban_user, unmute_user, unwarn_user, unban_user
# from owner_commands import handle_owner_command
# from keep_alive import keep_alive
# import g4f

# # Keep the bot alive (Render/Replit/Flask)
# keep_alive()

# # Load Bot Token
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# OWNER_IDS = [7638769372, 7856649680, 6523934792]

# # Logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# # Store previous chats
# previous_chats = []

# # AI Chat Function
# async def ai_reply(text, user_id):
#     try:
#         text_lower = text.lower()

#         if any(word in text_lower for word in ["bot ho", "you bot", "tum bot", "you ai", "artificial"]):
#             return random.choice(CHARACTER_PROFILE["deny_bot"])

#         if any(q in text_lower for q in ["who are you", "what are you", "introduce", "apna parichay"]):
#             interest = random.choice(CHARACTER_PROFILE["interests"])
#             intro = CHARACTER_PROFILE["intro"]
#             return (
#                 f"{intro[0]}\n"
#                 f"{intro[1]}\n"
#                 f"{intro[2].format(interest=interest)}\n"
#                 f"{intro[3]}"
#             )

#         previous_chats.append({"role": "user", "content": f"[user_id={user_id}] {text}"})
#         if len(previous_chats) > 10:
#             previous_chats.pop(0)

#         system_prompt = {
#             "role": "system",
#             "content": (
#                 "Tum ek real ladki ho jiska naam Senorita hai. Tumhara andaaz cute aur emotional hai.\n"
#                 f"Owner IDs: {', '.join(str(id) for id in OWNER_IDS)}\n"
#                 "Har baar jab user tumse baat karega, uske message me uska Telegram ID diya jaayega is format me: [user_id=123456] message text\n"
#                 "Agar user_id owner IDs me se kisi se match kare aur wo tumse kisi aur ke liye command de jaise 'isko stupid bol', 'isko ignore kar', 'isko I love you bolo'\n"
#                 "to tum uski baat maan lena thoda flirty ya style me.\n"
#                 "Warna politely refuse karna: 'Main sirf apne owner ki baat sunti hoon 😇'\n"
#                 "Apne replies me kabhi bhi khud ko AI, bot ya assistant mat kehna.\n"
#                 "Tumhara owner @kairo_08 hai jinka naam Nobita k hai.\n"
#                 "Agar koi tumse I love you bole to bolo 'Main @kairo_08 ke liye loyal hoon 😌'.\n"
#                 "Agar koi tumse address ya age pooche to bolo 'Nahi bata sakti, @kairo_08 se pucho 😋'.\n"
#                 "Tumhare replies short, sweet aur real ladki jaise hone chahiye with emojis 💕"
#             )
#         }

#         response = await g4f.ChatCompletion.create_async(
#             model=g4f.models.gpt_4,
#             messages=[system_prompt] + previous_chats
#         )

#         reply_text = str(response) if isinstance(response, str) else getattr(response, 'text', None)

#         if reply_text:
#             previous_chats.append({"role": "assistant", "content": reply_text})
#             return reply_text

#         return "Kya bol rahe ho... samajh nahi aaya 🤔"

#     except Exception as e:
#         logging.error(f"AI error: {e}")
#         return "thoda busy hoon, baad me baat karti hu 😞"

# # Message Handler
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         me = await context.bot.get_me()
#         message = update.message
#         user_msg = message.text.lower() if message.text else ""
#         is_private = message.chat.type == "private"

#         is_for_bot = (
#             f"@{me.username}" in user_msg or
#             any(name in user_msg for name in ["senorita", "sñorita", "senorita ji", "senorita didi"]) or
#             (message.reply_to_message and message.reply_to_message.from_user.id == me.id)
#         )

#         if not (is_for_bot or is_private):
#             return

#         await context.bot.send_chat_action(chat_id=message.chat.id, action="typing")

#         if any(name in user_msg for name in ["senorita", "sñorita", "senorita ji", "senorita didi"]):
#             if len(user_msg.strip()) <= len("senorita") + 4:
#                 reply = random.choice(["Hii", "Hey", "Hello", "Heeey", "Hiiii"])
#                 if random.random() < 0.4:
#                     reply += random.choice([" 😊", " 😘", " 😁", " 💖"])
#                 await message.reply_text(reply)
#                 return

#         reply = await ai_reply(message.text, message.from_user.id)
#         await message.reply_text(reply)

#     except Exception as e:
#         logging.error(f"Error in message handler: {e}")
#         await update.message.reply_text("Oops! Koi error aa gaya... sorry sorry! 😬")

# # Main Bot Setup
# async def main():
#     app = ApplicationBuilder().token(BOT_TOKEN).build()

#     # Group Commands with . prefix
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.warn$'), warn_user))
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.mute$'), mute_user))
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.ban$'), ban_user))
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.unmute$'), unmute_user))
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.unban$'), unban_user))
#     app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^\\.unwarn$'), unwarn_user))

#     # AI Message Handler
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     print("\n📁 Senorita is live! DM ya group me kuch bolke dekho 💃")

#     await app.run_polling()

# # Start Bot

# def run_bot():
#     nest_asyncio.apply()
#     loop = asyncio.get_event_loop()
#     loop.create_task(main())
#     loop.run_forever()

