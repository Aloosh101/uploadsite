from telethon import TelegramClient
import os

api_id = os.environ["TELE_API_ID"]
api_hash = os.environ["TELE_API_HASH"]


client = TelegramClient('session_name', api_id, api_hash)

client.start()


client.disconnect()
