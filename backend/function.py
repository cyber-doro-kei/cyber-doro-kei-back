#streamで変化を検知したときに使うやつ(まだ使ってない)(event関連で使うかも？)
def on_snapshot(keys, changes, docs):
    for change in changes:
        #変更されたドキュメントを取得
        doc_ref = change.document.reference
        
        #ドキュメントのデータを取得
        doc_data = change.document.to_dict()
        
        # room_idが受け取ったroom_idに一致する場合のみ処理を続行
        if doc_data.get("room_id") == received_room_id:
            # ユーザーの数を取得
            users_ref = db.collection("users").where("room_id", "==", received_room_id)
            users_snapshot = users_ref.get()
            total_users = len(users_snapshot)

            # is_copがfalseかつis_under_arrestがfalseなユーザーの数を取得
            non_cop_under_arrest_users_ref = users_ref.where("is_cop", "==", False).where("is_under_arrest", "==", False)
            non_cop_under_arrest_users_snapshot = non_cop_under_arrest_users_ref.get()
            non_cop_under_arrest_users_count = len(non_cop_under_arrest_users_snapshot)

            # 過半数以上の条件を満たしているか確認
            if non_cop_under_arrest_users_count > total_users / 2:
                # イベントログに"event start"を書き込む
                event_log_ref = db.collection("event_log").document(received_room_id)
                event_log_ref.set({
                    "event": "event start",
                    "timestamp": firestore.SERVER_TIMESTAMP
                })

                print("Event started successfully")

        # # 変更された中身を扱う
        # if change.type.name == 'ADDED':
        #     # 新しいものが追加されたとき
        #     data = change.document.to_dict()
        #     print(f"Added document: {data}")
        # elif change.type.name == 'MODIFIED':
        #     # 内容が修正されたとき
        #     data = change.document.to_dict()
        #     print(f"Modified document: {data}")
        # elif change.type.name == 'REMOVED':
        #     # なくなったとき
        #     print(f"Removed document: {change.document.id}")

        # FastAPIエンドポイントにデータを送信するか、データを直接処理する
        response = requests.post("http://localhost:8000/process_firestore_stream", json={"test_message": "test"})
        print(response.json())
        print("HTTP POST request successful")


# Cloud Firestoreの特定のコレクションを監視する
def watch_firestore(room_id: str):
    collection_ref = db.collection("rooms")
    query = collection_ref.where("room_id", "==", room_id)
    query_watch = query.on_snapshot(on_snapshot)