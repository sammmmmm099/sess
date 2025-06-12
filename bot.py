import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.all import layer
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded
)
from pyrogram.sessions import StringSession
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("StringBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text(
        "**Welcome to Pyrogram String Session Generator**\n\n"
        "Use /generate to begin."
    )


@bot.on_message(filters.command("generate") & filters.private)
async def generate(_, message: Message):
    try:
        ask = await message.reply_text("📥 Send your API ID:")
        api_id_msg = await bot.listen(message.chat.id)
        api_id = api_id_msg.text.strip()

        if not api_id.isdigit():
            await api_id_msg.reply("❌ Invalid API ID. Process canceled.")
            return

        ask = await message.reply_text("📥 Send your API HASH:")
        api_hash_msg = await bot.listen(message.chat.id)
        api_hash = api_hash_msg.text.strip()

        ask = await message.reply_text("📞 Send your phone number with country code (e.g., +123456789):")
        phone_msg = await bot.listen(message.chat.id)
        phone = phone_msg.text.strip()

        app = Client(
            name="gen_session",
            api_id=int(api_id),
            api_hash=api_hash,
            in_memory=True,
            session_string=StringSession()
        )

        await app.connect()
        sent_code = await app.send_code(phone)

        ask = await message.reply("📨 Enter the OTP sent to your Telegram:")
        otp_msg = await bot.listen(message.chat.id)
        otp_code = otp_msg.text.strip()

        try:
            await app.sign_in(phone_number=phone, phone_code=otp_code, phone_code_hash=sent_code.phone_code_hash)
        except PhoneCodeInvalid:
            await message.reply("❌ Invalid OTP. Try again.")
            await app.disconnect()
            return
        except PhoneCodeExpired:
            await message.reply("❌ OTP expired. Try again.")
            await app.disconnect()
            return
        except SessionPasswordNeeded:
            await message.reply("⚠️ Account has 2FA enabled. This bot does not support 2FA.")
            await app.disconnect()
            return

        string_session = app.export_session_string()
        me = await app.get_me()
        await app.send_message(
            "me",
            f"✅ Your Pyrogram String Session:\n\n`{string_session}`\n\n"
            f"📛 Name: {me.first_name}\n📱 ID: {me.id}\n\n⚠️ Keep it safe!"
        )
        await app.disconnect()
        await message.reply("✅ Session string has been sent to your Saved Messages.")

    except ApiIdInvalid:
        await message.reply("❌ Invalid API ID or API HASH.")
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")


print("Pyrogram String Generator Bot Running...")
bot.run()
