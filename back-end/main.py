from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fun import AESCipher, FileMerger, TeleSql
from pydantic import BaseModel
import tempfile
import os

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

# telegram target and encryption key
target = "@hiasrf"
encryption_key = "slmle?43718slmle#$%!?slmle@#~slmle"


@app.post('/api/data')
async def data_storage(mydata: MyData):

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
            
            #connect telegramapi
            client = TeleSql(target, session="session_name.session", api_id=25153583, api_hash="35543407ec1e319a3927f267183adb5d")
            client = await client.connect()

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
            
            #clear id_tele and disconnect
            del id_tele[id]
            client.disconnect()

            return {"token": token}
    
    #if less than data
    elif len(data_list[id]) >= data_parts:
            
            #connect telegramapi
            client = TeleSql(target, session="session_name.session", api_id=25153583, api_hash="35543407ec1e319a3927f267183adb5d")
            client = await client.connect()
            
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

            #disconnect
            client.disconnect()
            del data_list[id]
    return {"message": "Data received successfully"}