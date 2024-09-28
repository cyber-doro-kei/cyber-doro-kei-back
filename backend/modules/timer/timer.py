from datetime import datetime


class Timer:
    """
    Timer: Class -> 時間管理全体を統括するクラス
    """

    def __init__(self, db, room_id, jst) -> None:
        self.db = db
        self.room_id: str = room_id
        self.jst = jst

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
        doc_ref = self.db.collection("rooms").document(self.room_id)
        # DEBUG:
        print(f"room_id: {self.room_id}")
        doc_ref.update(data)

    def finish_timer(self) -> None:
        """
        description: タイマーを終了(ゲームを終了)
        -----------------
        none
        -----------------
        return none
        """

        rooms_ref = self.db.collection("rooms")
        room_ref = rooms_ref.document(self.room_id)
        
        room_ref.update({"is_active": False})
        # COMMENT: 今後ゲーム終了時に何かしらDBを書き換えたい場合、ここに追記すればよい
