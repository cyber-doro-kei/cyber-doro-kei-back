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

#.envファイルから環境変数を読み込む
load_dotenv()

#環境変数からFirebaseの秘密鍵ファイルのパスを取得
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")

#Firebase初期化
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 日本時間のタイムゾーンを取得
jst = pytz.timezone('Asia/Tokyo')

#steramで変化を検知したときに使うやつ(まだ使ってない)(event関連で使うかも？)
def on_snapshot(keys, changes,docs,):
    print(f"keys : {keys}")
    print(f"docs: {docs}")
    print(f"changes: {changes}")
    for change in changes:
        # 変更された中身を扱う
        if change.type.name == 'ADDED':
            # 新しいものが追加されたとき
            data = change.document.to_dict()
            print(f"Added document: {data}")
        elif change.type.name == 'MODIFIED':
            # 内容が修正されたとき
            data = change.document.to_dict()
            print(f"Modified document: {data}")
        elif change.type.name == 'REMOVED':
            # なくなったとき
            print(f"Removed document: {change.document.id}")

        # FastAPIエンドポイントにデータを送信するか、データを直接処理する
        response = requests.post("http://localhost:8000/process_firestore_stream", json={"test_message": "test"})
        print(response.json())
        print("HTTP POST request successful")
        
# Cloud Firestoreの特定のコレクションを監視する(まだ使ってない)(event関連で使うかも？)
collection_ref = db.collection("rooms")
docs_watch = collection_ref.on_snapshot(on_snapshot)


class StartTimer(BaseModel):
    is_admin: bool
# test用クラス
class Item(BaseModel):
    test_message: str
    
app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "hello world!"}

@app.get("/hello1")
async def hello():
    return {"message": "hello world!2"}

@app.post("/start/assign/{room_id}")
async def assign_member(room_id: str):
    if room_id == None:
        response = {"response": "Invalid input"}
        return JSONResponse(status_code=405, content=response)
    else:
        try:
            #usersコレクションを取得
            users_ref = db.collection("users")
            
            #room_idが等しいuserを取得
            users = users_ref.where("room_id", "==", room_id).stream()
            
            female_users = users_ref.where("room_id", "==", room_id).where("is_male", "==", False).count()
            male_users = users_ref.where("room_id", "==", room_id).where("is_male", "==", True).count() 
            male_cop = 0
            femal_cop = 0
            
            #copの設定人数を取り出す
            doc_ref = db.collection("rooms").document(room_id)
            doc_snapshot = doc_ref.get()
            cop_num = doc_snapshot.get("cop_num")
            
            # is_copをtrueにする人数を決定
            min_cop_count = min(male_users, female_users)
            cop_count = min(min_cop_count, cop_num // 2)
            
            # is_copをtrueに設定
            users_ref = db.collection("users").where("room_id", "==", room_id)
            users = users_ref.stream()
            count = 0
            for user in users:
                if count < cop_count:
                    user_ref = db.collection("users").document(user.id)
                    user_ref.update({"is_cop": True})
                    count += 1
                else:
                    user_ref = db.collection("users").document(user.id)
                    user_ref.update({"is_cop": False})
            
            # cop_count分だけis_copをtrueにした後、残りの人をfalseに設定
            users = db.collection("users").where("room_id", "==", room_id).where("is_cop", "==", False).stream()
            for user in users:
                user_ref = db.collection("users").document(user.id)
                user_ref.update({"is_cop": False})
            # for user in users:
            #     user_data = user.to_dict()
            #     user_ref = users_ref.document(user.id)
            #     is_male = user_data.get("is_male", False)
            #     if is_male:
            #         if male_cop <= male_users * 0.4:
            #             male_cop += 1
            #             user_ref = users_ref.document(user.id)
            #             user_ref.update({"is_cop": True})
            #         else:
            #             user_ref = users_ref.document(user.id)
            #             user_ref.update({"is_cop": False})
            #     else:
            #         if male_cop <= (total_users - male_users)* 0.4:
            #             female_cop += 1
            #             user_ref = users_ref.document(user.id)
            #             user_ref.update({"is_cop": True})
            #         else:
            #             user_ref = users_ref.document(user.id)
            #             user_ref.update({"is_cop": False})
            
            # # is_maleがtrueの場合
            # male_cop_count = int(total_users * 0.4)
            # male_cop_count = int(male_cop_count)
            # users_ref.where("room_id", "==", room_id).where("is_male", "==", True).limit(male_cop_count).update({"is_cop": True})
            # users_ref.where("room_id", "==", room_id).where("is_male", "==", True).offset(male_cop_count).update({"is_cop": False})
            
            # # is_maleがfalseの場合
            # female_cop_count = int(total_users * 0.4)
            # users_ref.where("room_id", "==", room_id).where("is_male", "==", False).limit(female_cop_count).update({"is_cop": True})
            # users_ref.where("room_id", "==", room_id).where("is_male", "==", False).offset(female_cop_count).update({"is_cop": False})
            
            # user_ref = users_ref.document(user.id)
            # user_ref.update({"is_cop": True})
            response = {"response": "is_cop field updated successfully"}
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
                "started_at": started_at
            }

            # Firebaseのroomsコレクションへの参照を取得し、指定されたドキュメントにデータを追加
            collection_ref = db.collection("rooms")
            doc_ref = collection_ref.document(room_id)
            doc_ref.update(data)

            return {"message": "Data added to Firebase successfully"}

        except Exception as e:
            # エラーが発生した場合はHTTP例外を発生させる
            raise HTTPException(status_code=500, detail=f"Error adding data to Firebase: {str(e)}")
            # response = {"response": "Successful Operation"}
            # return JSONResponse(status_code=200, content=response)

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
