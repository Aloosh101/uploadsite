from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fun import AESCipher, FileMerger, TeleSql
from pydantic import BaseModel
from io import BytesIO

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

datalist = {} 
IDtele = {}
target = "https://t.me/hiasrf"
encryption_key = "slmle?43718slmle#$%!?slmle@#~slmle"

@app.post('/api/data')
async def handle_data(mydata: MyData):
    print(f"Received Data: {mydata}")

    id = mydata.id
    data = mydata.data
    message = mydata.message

    if id not in datalist:
        datalist[id] = []

    datalist[id].append(data)
    print(len(datalist[id]))
    if message == "done":
            print(f"Data for ID {id} is done: {datalist[id]}")
            client = TeleSql(target, session="session_name.session", api_id=25153583, api_hash="35543407ec1e319a3927f267183adb5d")
            client = await client.connect()
            merger = FileMerger(datalist[id]).merge_data()
            encrypte = AESCipher(encryption_key).encrypt_string(str(merger))
            file_path = BytesIO(encrypte.encode("utf-8"))
            IDmessage = TeleSql.FileHandling(client).upload_file(file_path)
            del datalist[id]
            IDtele[id].append(IDmessage)
            token = AESCipher(encryption_key).decrypt_string(",".join(IDtele[id]))
            del IDtele[id]
            return token
    elif len(datalist[id]) == 10:
            print(f"Data for ID {id} is full: {datalist[id]}")
            client = TeleSql(target, session="session_name.session", api_id=25153583, api_hash="35543407ec1e319a3927f267183adb5d")
            client = await client.connect()
            merger = FileMerger(datalist[id]).merge_data()
            encrypte = AESCipher(encryption_key).encrypt_string(str(merger))
            file_path = BytesIO(encrypte.encode("utf-8"))
            IDmessage = TeleSql.FileHandling(client).upload_file(file_path)
            if id not in IDtele:
                IDtele[id] = []
            IDtele[id].append(IDmessage)
            del datalist[id]

    return {"message": "Data received successfully"}