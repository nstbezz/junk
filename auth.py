"""
Two-step auth helper.
Step 1: python auth.py send      -- sends the code to your phone
Step 2: python auth.py verify 12345  -- submits the code and saves session
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
PHONE = os.environ["TELEGRAM_PHONE"]
SESSION_FILE = "telegram_session"


async def send_code():
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    result = await client.send_code_request(PHONE)
    print(f"Code sent to {PHONE}. Phone code hash: {result.phone_code_hash}")
    # Save hash for verify step
    with open(".phone_code_hash", "w") as f:
        f.write(result.phone_code_hash)
    await client.disconnect()
    print("Now run: python auth.py verify <code>")


async def verify_code(code: str):
    with open(".phone_code_hash") as f:
        phone_code_hash = f.read().strip()
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    try:
        await client.sign_in(PHONE, code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        pwd = input("Two-step verification password: ")
        await client.sign_in(password=pwd)
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    await client.disconnect()
    print("Session saved. You can now run: python read_chats.py")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "send":
        asyncio.run(send_code())
    elif sys.argv[1] == "verify" and len(sys.argv) == 3:
        asyncio.run(verify_code(sys.argv[2]))
    else:
        print("Usage:\n  python auth.py send\n  python auth.py verify <code>")
