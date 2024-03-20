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
        doc_ref.update(data)
