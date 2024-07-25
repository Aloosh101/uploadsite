from telethon import TelegramClient
from typing import Union
import os
from logging import basicConfig, INFO, info, error

client: TelegramClient
entity: Union[str, int]

basicConfig(level=INFO)

def get_file_size(file_path):
    try:
        file_size = os.path.getsize(file_path)
        info(f"I got the file size: {file_size}")
        return file_size
    except FileNotFoundError:
        error(f"File '{file_path}' not found.")
    except Exception as e:
        error(f"Error getting file size: {e}")

class TeleSql:
    def __init__(self, name: Union[str, int], session: str, api_id: int, api_hash: str) -> None:
        global entity
        entity = name
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash
    async def connect(self):
        try:
            client = TelegramClient(session=self.session, api_id=self.api_id, api_hash=self.api_hash)
            await client.connect()
            
            info("Connected to Telegram")
            return client
        except Exception as e:
            error(f"Failed to connect to Telegram: {e}")
            return None
    async def disconnect():
        try:
            await client.disconnect()
            info("Disconnected from Telegram")
        except Exception as e:
            error(f"Failed to disconnect from Telegram: {e}")
            return None

    class FileHandling:
        def __init__(self,client: TelegramClient) -> None:
            self.client = client

        async def upload_file(self,file_path):
            try:
                res = await self.client.send_file(
                    entity=entity,
                    file=file_path,
                    file_size=get_file_size(file_path))
                message_id = res.id + 1
                info(f"Sent file '{file_path}' to {entity}")
                return message_id
            
            except Exception as e:
                error(f"Failed to send file: {e}")
                return None
        
        async def download_file(self,message_id: int, path: str):
            try:
                async for message in self.client.iter_messages(entity,offset_id=message_id,limit=1):#,max_id=message_id,min_id=message_id,limit=1):
                    #print(message.id, message.text)
                    path = await message.download_media(file=path)
                    info(f"Downloaded file to {path}")
                    return path
    
            except Exception as e:
                error(f"Failed to download file: {e}")
                return None

    class DataHandling:
        def __init__(self,client: TelegramClient) -> None:
            self.client = client

        async def send_message(self,message: str):
            try:
                res = await self.client.send_message(entity=entity,message=message)
                message_id = res.id + 1
                info(f"Sent message '{res.text}' to {entity}")
                return message_id
            
            except Exception as e:
                error(f"Failed to send message: {e}")
                return None
        async def get_message(self,message_id):
            try:
                async for message in self.client.iter_messages(entity,offset_id=message_id,limit=1):#,max_id=message_id,min_id=message_id,limit=1):
                    #print(message.id)#, message.text)
                    info(f"Get message '{message}' from {entity}")
                    return message.text

            except Exception as e:
                error(f"Failed to get message: {e}")
