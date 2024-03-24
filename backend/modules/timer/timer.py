from datetime import datetime

def listener(event):
    print(event.event_type)  # can be 'put' or 'patch'
    print(event.path)  # relative to the reference, it seems
    print(event.data)  # new data at /reference/event.path. None if deleted

class Timer:
    """
    Timer: Class -> 時間管理全体を統括するクラス
    """

    def __init__(self, client, room_id, jst, db) -> None:
        self.client = client
        self.room_id: str = room_id
        self.jst = jst
        self.db = db

    def start_timer(self) -> None:
        """
        description: タイマーを開始
        -----------------
        none
        -----------------
        return none
        """

        started_at = datetime.now(self.jst).isoformat()
        data = {"started_at": started_at, "is_active": True}

        # COMMENT: Firebaseのroomsコレクションへの参照を取得し、指定されたドキュメントにデータを追加
        doc_ref = self.client.collection("rooms").document(self.room_id)
        doc_ref.update(data)
        self.db.reference().listen(listener)
