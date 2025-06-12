import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    PasswordRequiredError
)
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

Optimus = TelegramClient(
    session="OptimusPrime",
    api_id=API_ID,
    api_hash=API_HASH
).start(bot_token=BOT_TOKEN)

@Optimus.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.sender_id
    username = event.sender.username or "N/A"
    first_name = event.sender.first_name or "N/A"
    last_name = event.sender.last_name or "N/A"
    start_message = f"""
👋 Hello {first_name}, I am a **Telethon String Session Generator Bot**.

⚠️ Store your session string securely. Anyone with it can access your Telegram account!

🔐 Your Info:
➤ TG ID: `{user_id}`
➤ Username: `{username}`
➤ Name: `{first_name} {last_name}`
"""
    await event.respond(start_message)

@Optimus.on(events.NewMessage(pattern="/generate"))
async def generate_string_session_command(event):
    try:
        async with Optimus.conversation(event.chat_id, timeout=300) as conv:
            await conv.send_message("📥 Please send your **API ID**:")
            your_api_id = await conv.get_response()

            if not your_api_id.text.isdigit():
                await conv.send_message("❌ Invalid API ID. Please enter a valid number.")
                return

            await conv.send_message("📥 Now, send your **API HASH**:")
            your_api_hash = await conv.get_response()

            await conv.send_message("📞 Now send your **phone number with country code** (e.g., +123456789):")
            your_phone_number = await conv.get_response()

            try:
                Prime = TelegramClient(StringSession(), api_id=int(your_api_id.text), api_hash=your_api_hash.text)
                await Prime.connect()

                await Prime.send_code_request(phone=your_phone_number.text)
                await conv.send_message("📨 Please send the **OTP** you received:")
                otp_code = await conv.get_response()

                try:
                    await Prime.sign_in(phone=your_phone_number.text, code=otp_code.text)

                except (PasswordRequiredError, SessionPasswordNeededError):
                    await conv.send_message("🔐 Your account has **2FA enabled**. Please send your **password**:")
                    password = await conv.get_response()

                    try:
                        await Prime.sign_in(password=password.text)
                    except PasswordHashInvalidError:
                        await conv.send_message("❌ Invalid password. Session cancelled. Use /generate to try again.")
                        return

                session_string = Prime.session.save()
                me = await Prime.get_me()
                text = f"""
👋 Hello {me.first_name},

Here is your **Telethon String Session**:

