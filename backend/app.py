import math
import random
import subprocess
from datetime import datetime

import pytz
from assign.assign import Assign
from db import DB
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from models import Item, StartTimer

# COMMENT: Firebase初期化
db_init = DB()
db = db_init.connection()
    
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
        assign.execute()
        response = {"response": "is_cop field updated successfully for matching documents"}
        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        # エラーが発生した場合はHTTP例外を発生させる
        raise HTTPException(status_code=500, detail=f"Error updating documents: {str(e)}")

@app.post("/start/timer/{room_id}")
async def start_timer(room_id: str, req: StartTimer):
    try:
        # ドキュメントに追加するデータを準備
        started_at = datetime.now(jst).isoformat()
        data = {
            "started_at": started_at,
            "is_active" : True
        }

        # Firebaseのroomsコレクションへの参照を取得し、指定されたドキュメントにデータを追加
        doc_ref = db.collection("rooms").document(room_id)
        doc_ref.update(data)

        command = ['python','event/execute.py', room_id]
        subprocess.Popen(command) # COMMENT: サブプロセスでDB監視を実施

        return {"message": "Data added to Firebase successfully"}

    except Exception as e:
        # エラーが発生した場合はHTTP例外を発生させる
        raise HTTPException(status_code=500, detail=f"Error adding data to Firebase: {str(e)}")
