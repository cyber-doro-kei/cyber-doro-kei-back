from datetime import datetime
import time
from google.cloud import firestore

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

        # started_at = datetime.now(self.jst).isoformat()
        started_at = firestore.SERVER_TIMESTAMP
        data = {"started_at": started_at}

        # COMMENT: Firebaseのroomsコレクションへの参照を取得し、指定されたドキュメントにデータを追加
        doc_ref = self.db.collection("rooms").document(self.room_id)
        # DEBUG:
        print(f"room_id: {self.room_id}")
        doc_ref.update(data)
        time.sleep(0.1)
        is_active_true = {"is_active": True}
        doc_ref.update(is_active_true)

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

    def execute_timer(self) -> None:
        """
        description: 指定時間になったらタイマーを終了(is_activeをFalseにする)
        -----------------
        none
        -----------------
        return none
        """
        try:
            # roomのドキュメントを取得
            room_ref = self.db.collection("rooms").document(self.room_id)
            room_data = room_ref.get().to_dict()
            
            if not room_data:
                print(f"Room {self.room_id} not found")
                return

            play_time_seconds = room_data.get("play_time_seconds", 0)
            if not play_time_seconds:
                print("play_time_seconds not set")
                return

            # 終了時刻を計算（現在時刻から指定時間後）
            start_time = time.time()
            end_time = start_time + (play_time_seconds * 60)

            while time.time() < end_time:
                # 1秒ごとにis_activeをチェック
                current_room = room_ref.get().to_dict()
                
                # ゲームが既に終了している場合（finish_timerが呼ばれた場合など）
                if not current_room.get("is_active", False):
                    print("Game ended early")
                    return
                    
                time.sleep(1)

            # 指定時間が経過したらis_activeをfalseに設定
            room_ref.update({"is_active": False})
            print(f"Game ended after {play_time_seconds} minutes")

        except Exception as e:
            print(f"Error in start_timer: {e}")
            # エラーが発生した場合もis_activeをfalseに設定
            try:
                room_ref = self.db.collection("rooms").document(self.room_id)
                room_ref.update({"is_active": False})
            except Exception as e2:
                print(f"Error updating is_active: {e2}")