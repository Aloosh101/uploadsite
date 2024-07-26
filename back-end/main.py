import asyncio
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import AESCipher, FileMerger, TeleSql
from pydantic import BaseModel
import tempfile
import os
import uvicorn

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReceivedData(BaseModel):
    user_id: str
    data_chunk: str
    status_message: str


# Initialize data structures and environment variables
data_chunks_by_user = {} 
max_data_chunks_per_user = 10
user_telegram_ids = {}

target = os.environ['USERNAME_TARGET'] 
encryption_key = os.environ['PRIVATE_ENCRYPTION_KET']
api_id = os.environ["TELE_API_ID"]
api_hash = os.environ["TELE_API_HASH"]
client = None

async def connect_to_telegram():
    global client
    client = TeleSql(target, session="session_name.session", api_id=api_id, api_hash=api_hash)
    client = await client.connect()


async def handle_data_chunk(user_id: str, data_chunk: str) -> None:
    if user_id not in data_chunks_by_user:
        data_chunks_by_user[user_id] = []

    data_chunks_by_user[user_id].append(data_chunk)


async def process_data_chunks(user_id: str, file_name: str) -> str:
    data_chunks = data_chunks_by_user.pop(user_id)
    merged_data = FileMerger(data_chunks).merge_data()
    encrypted_data = AESCipher(encryption_key).encrypt_string(str(merged_data))

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(encrypted_data.encode("utf-8"))
    temp_file.close()

    telegram_message_id = await TeleSql.FileHandling(client).upload_file(temp_file.name)
    os.remove(temp_file.name)

    if user_id not in user_telegram_ids:
        user_telegram_ids[user_id] = []

    user_telegram_ids[user_id].append(str(telegram_message_id))

    return file_name


@app.post('/api/data')
async def receive_data(received_data: ReceivedData, 
                        password: Optional[str] = None, 
                        file_name: Optional[str] = None):
    if not client: await connect_to_telegram()

    user_id = received_data.user_id
    data_chunk = received_data.data_chunk
    status_message = received_data.status_message

    await handle_data_chunk(user_id, data_chunk)

    if status_message == "done":
        if not file_name:
            return {"error": "No file name provided"}

        file_name = await process_data_chunks(user_id, file_name)
        token = generate_token(user_telegram_ids[user_id], file_name, password)
        user_telegram_ids.pop(user_id)

        return {"token": token}

    elif len(data_chunks_by_user[user_id]) >= max_data_chunks_per_user:
        file_name = await process_data_chunks(user_id, file_name)

    return {"message": "Data received successfully"}


@app.get("/api/data")
async def retrieve_data(token: str):
    if not client: await connect_to_telegram()

    decrypted_token = decrypt_token(token)
    user_ids, file_name = decrypted_token

    # Retrieve data from Telegram using user_ids and file_name

    return {"":""}


def generate_token(user_ids: list, file_name: str, password: Optional[str] = None) -> str:
    encryption_key_to_use = password if password else encryption_key
    ids_string = ",".join(user_ids)
    token_data = {"ids": ids_string, "file_name": file_name}
    token = AESCipher(encryption_key_to_use).encrypt_string(str(token_data))
    return token


def decrypt_token(token: str, password: Optional[str] = None) -> tuple:
    encryption_key_to_use = password if password else encryption_key
    decrypted_token = AESCipher(encryption_key_to_use).decrypt_string(token)
    token_data = eval(decrypted_token)
    user_ids = token_data["ids"].split(",")
    file_name = token_data["file_name"]
    return user_ids, file_name


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)