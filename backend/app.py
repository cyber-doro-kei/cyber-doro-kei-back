import subprocess

import pytz
from db import DB
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from models import StartTimer
from modules.assign.assign import Assign
from modules.timer.timer import Timer

# COMMENT: Firebase初期化
db_init = DB()
client, db = db_init.connection()
    
# 日本時間のタイムゾーンを取得
jst = pytz.timezone('Asia/Tokyo')

app = FastAPI()


@app.get("/")
async def hello():
    return {"message": "hello world!"}


@app.post("/start/assign/{room_id}")
async def assign_member(room_id: str):
    try:
        assign = Assign(db, room_id)
        assign.assign_member()

        response = {"response": "is_cop field updated successfully for matching documents"}
        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        # エラーが発生した場合はHTTP例外を発生させる
        raise HTTPException(status_code=500, detail=f"Error updating documents: {str(e)}")


@app.post("/start/timer/{room_id}")
async def start_timer(room_id: str):
    try:
        timer = Timer(client, room_id, jst, db)
        timer.start_timer()

        command = ['python','modules/event/execute.py', room_id]
        # subprocess.Popen(command) # COMMENT: サブプロセスでDB監視を実施

        response = {"message": "Data added to Firebase successfully"}
        return JSONResponse(status_code=200, content=response)
        
    except Exception as e:
        # エラーが発生した場合はHTTP例外を発生させる
        raise HTTPException(status_code=500, detail=f"Error adding data to Firebase: {str(e)}")
