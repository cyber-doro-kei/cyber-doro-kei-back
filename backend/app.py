import math
import random
import subprocess
from datetime import datetime

import pytz
from db import DB
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

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
    if room_id == None:
        response = {"response": "Invalid input"}
        return JSONResponse(status_code=405, content=response)
    else:
        try:
            # usersコレクションの参照を取得
            users_ref = db.collection("users")
            
            #copの設定人数を取り出す
            doc_ref = db.collection("rooms").document(room_id)
            doc_snapshot = doc_ref.get()
            cop_ration = doc_snapshot.get("cop_num")
            robber_ration = doc_snapshot.get("robber_num")
            
            # ドキュメントを取得し、room_idフィールドが指定されたroom_idと等しい場合はis_copフィールドを更新する
            users = users_ref.where("room_id", "==", room_id).stream()
            users_list = list(users)
            users_num = len(users_list)
            # userをシャッフルする
            random.shuffle(users_list)
            
            #警察にいれる人数を計算
            cop_num = math.floor((cop_ration / (cop_ration + robber_ration)) * users_num)
            
            for user in users_list:
                user_ref = users_ref.document(user.id)
                if cop_num > 0:
                    user_ref.update({"is_cop": True})
                    cop_num -= 1
                else:
                    user_ref.update({"is_cop": False})
            
            response = {"response": "is_cop field updated successfully for matching documents"}
            return JSONResponse(status_code=200, content=response)

        except Exception as e:
            # エラーが発生した場合はHTTP例外を発生させる
            raise HTTPException(status_code=500, detail=f"Error updating documents: {str(e)}")

@app.post("/start/timer/{room_id}")
#room_idは
async def start_timer(room_id: str):
    if room_id == None:
        response = {"response": "Invalid input"}
        return JSONResponse(status_code=405, content=response)
    else:
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


@app.post("/event/start/{room_id}")
async def event_start(room_id: str):
    if room_id == None:
        response = {"response": "Invalid input"}
        return JSONResponse(status_code=405, content=response)
    else:
        response = {"response": "Successful Operation"}
        return JSONResponse(status_code=200, content=response)

@app.post("/event/finish/{room_id}")
async def event_finish(room_id: str):
    if room_id == None:
        response = {"response": "Invalid input"}
        return JSONResponse(status_code=405, content=response)
    else:
        response = {"response": "Successful Operation"}
        return JSONResponse(status_code=200, content=response)
