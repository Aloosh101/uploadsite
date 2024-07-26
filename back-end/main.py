import asyncio
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

class MyData(BaseModel):
    id: str
    data: str
    message: str

# initiate data list and data parts and telegram api
data_list = {} 
data_parts = 10
id_tele = {}

# Environment variables
target = os.environ['USERNAME_TARGET'] 
encryption_key = os.environ['PRIVATE_ENCRYPTION_KET']
api_id = os.environ["TELE_API_ID"]
api_hash = os.environ["TELE_API_HASH"]
client = None

async def connect():
    global client
    client = TeleSql(target, session="session_name.session", api_id=api_id, api_hash=api_hash)
    client = await client.connect()




@app.post('/api/data')
async def files_storage(mydata: MyData):
    if not client:
        await connect()
    #check if id exist
    id = mydata.id
    data = mydata.data
    message = mydata.message

    #check if id in id_tele
    if id not in data_list:
        data_list[id] = []

    #append data
    data_list[id].append(data)

    #All data has been sent
    if message == "done":
            

            #handle data
            merger = FileMerger(data_list[id]).merge_data()
            encrypte = AESCipher(encryption_key).encrypt_string(str(merger))
            
            #temp file
            file_path = tempfile.NamedTemporaryFile(delete=False)
            file_path.write(encrypte.encode("utf-8"))
            file_path.close()
            
            #send to telegram
            id_message = await TeleSql.FileHandling(client).upload_file(file_path.name)
            
            #delete temp file
            os.remove(file_path.name)
            
            #clear data_list 
            del data_list[id]

            #save ID message
            if id not in id_tele:
                id_tele[id] = []
            id_tele[id].append(str(id_message))

            #encrypt ids and create token
            token = AESCipher(encryption_key).encrypt_string(",".join(id_tele[id]))
            
            #clear id_tele
            del id_tele[id]


            return {"token": token}
    
    #if less than data
    elif len(data_list[id]) >= data_parts:
                                 
            #handle data
            merger = FileMerger(data_list[id]).merge_data()
            encrypte = AESCipher(encryption_key).encrypt_string(str(merger))
            
            #temp file
            file_path = tempfile.NamedTemporaryFile(delete=False)
            file_path.write(encrypte.encode("utf-8"))
            file_path.close()
            
            #send to telegram
            id_message = await TeleSql.FileHandling(client).upload_file(file_path.name)
            os.remove(file_path.name)
            
            #clear data_list
            if id not in id_tele:
                id_tele[id] = []                
 
            #save ID message
            id_tele[id].append(str(id_message))


            del data_list[id]

    return {"message": "Data received successfully"}

@app.get("/api/data")
async def files_get(token: str):
    if not client:
        await connect()
    #decrypt token
    decrypted_token = AESCipher(encryption_key).decrypt_string(token)
    ids = decrypted_token.split(",")
    

    
    return {"":""}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
