from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from datetime import datetime
import pytz
from models import Item,StartTimer 
from function import on_snapshot
import random
import math

#.envファイルから環境変数を読み込む
load_dotenv()

#環境変数からFirebaseの秘密鍵ファイルのパスを取得
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")

#Firebase初期化
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
    
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
async def start_timer(room_id: str, req: StartTimer):
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
            collection_ref = db.collection("rooms")
            doc_ref = collection_ref.document(room_id)
            doc_ref.update(data)

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
