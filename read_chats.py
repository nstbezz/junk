"""
Telegram chat reader using Telethon (MTProto user account).

Setup:
1. Copy .env.example to .env and fill in your credentials
2. Get API_ID and API_HASH from https://my.telegram.org/apps
3. Run: pip install -r requirements.txt
4. Run: python read_chats.py
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel

load_dotenv()

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
PHONE = os.environ["TELEGRAM_PHONE"]

SESSION_FILE = "telegram_session"


def format_sender(sender) -> str:
    if isinstance(sender, User):
        name = " ".join(filter(None, [sender.first_name, sender.last_name]))
        return f"{name} (@{sender.username})" if sender.username else name
    if isinstance(sender, (Chat, Channel)):
        return sender.title
    return "Unknown"


async def list_recent_messages(client: TelegramClient, limit: int = 5) -> None:
    """Print the most recent message from each dialog."""
    print("\n--- Recent messages from your chats ---\n")
    async for dialog in client.iter_dialogs():
        chat_name = dialog.name or "Unnamed"
        msg = dialog.message
        if msg and msg.text:
            preview = msg.text[:80].replace("\n", " ")
            print(f"[{chat_name}] {preview}")
    print()


async def listen_for_new_messages(client: TelegramClient) -> None:
    """Listen and print all incoming messages in real time."""
    print("Listening for new messages (Ctrl+C to stop)...\n")

    @client.on(events.NewMessage)
    async def handler(event):
        sender = await event.get_sender()
        chat = await event.get_chat()
        chat_name = getattr(chat, "title", None) or format_sender(sender)
        sender_name = format_sender(sender)
        text = event.message.text or "<media>"
        print(f"[{chat_name}] {sender_name}: {text}")

    await client.run_until_disconnected()


async def main() -> None:
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

    await client.start(phone=PHONE)
    print("Connected to Telegram.")

    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")

    await list_recent_messages(client)
    await listen_for_new_messages(client)


if __name__ == "__main__":
    asyncio.run(main())
