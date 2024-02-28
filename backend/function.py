#streamで変化を検知したときに使うやつ(まだ使ってない)(event関連で使うかも？)
def on_snapshot(keys, changes, docs):
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
 