import time
from datetime import datetime, timedelta


class Event:
    """
    Event: Class -> イベント全体を統括するクラス
    """

    def __init__(self, db, room_id: str) -> None:
        self.db = db
        self.room_id: str = room_id
        self.robber_num = 0
        self.started_at = None
        self.play_time = None

    def count_robber_num(self) -> None:
        """
        description: 逃走者の人数カウント
        -------------------
        none
        -------------------
        return: None
        """

        room_ref = self.db.collection("rooms").document(self.room_id)
        room_snapshot = room_ref.get()
        self.robber_num: int = room_snapshot.get("robber_num")

    def get_game_info(self) -> None:
        """
        description: ゲーム開始時刻とプレイ時間を取得する
        -------------------
        none
        -------------------
        return: None
        """
        room_ref = self.db.collection("rooms").document(self.room_id)
        room_snapshot = room_ref.get()
        room_data = room_snapshot.to_dict()
        if room_data:
            self.started_at = room_data.get("started_at")
            if self.started_at:
                self.started_at = self.started_at.replace(tzinfo=None)
            self.play_time = room_data.get("play_time_seconds")
        else:
            print(f"No data found for room {self.room_id}")
        
    def is_event_start(self) -> bool:
        """
        description: イベントを開始するか否かの条件判定
        -------------------
        none
        -------------------
        return: boolean -> イベントを開始するかどうかのフラグ
        """

        self.count_robber_num()
        arrest_num: int = 0

        users_ref = self.db.collection("users")
        users = users_ref.where("room_id", "==", self.room_id).stream()
        for user in users:
            user_ref = users_ref.document(user.id)
            user_snapshot = user_ref.get()
            is_under_arrest: bool = user_snapshot.get("is_under_arrest",False)
            if is_under_arrest:
                arrest_num += 1
                
        # COMMENT: プレイ時間が半数経過でイベント発令
        self.get_game_info()
        time_elapsed = datetime.now() - self.started_at
        half_time_passed = time_elapsed >= timedelta(seconds=self.play_time // 2)

        if (
            self.robber_num // 2 <= arrest_num or half_time_passed
        ):  # COMMENT: 半数以上が逮捕されたらイベント発令
            return True
        else:
            return False
    
    def is_game_continue(self) -> bool:
        """
        description: ゲームが行われているかを判定する
        -------------------
        none
        -------------------
        return: boolean -> ゲームが続行中か否かのフラグ Trueの場合、ゲームが続行中であると見なす
        """

        doc_ref = self.db.collection("rooms").document(self.room_id)
        doc_snapshot = doc_ref.get()
        is_active: bool = doc_snapshot.get("is_active")

        return is_active

    def add_event_logs(self) -> None:
        """
        description: event_logsにイベントを追加
        -------------------
        none
        -------------------
        return: none
        """

        data = {
            "room_id": self.room_id,
            "event_name": "テストイベント",
            "event_output": "",
        }
        event_logs_ref = self.db.collection("event_logs")
        doc_ref = event_logs_ref.document(self.room_id)
        # ドキュメントが存在するか確認
        if doc_ref.get().exists:
            doc_ref.update(data)
        else:
            # ドキュメントが存在しない場合は新規作成
            doc_ref.set(data)
            
        doc_ref.update(data)

    def check_db(self) -> bool:
        """
        description: データベースを確認しにいく処理
        -------------------
        none
        -------------------
        return: boolean -> イベントを開始したか否かのフラグ Trueの場合DBの監視を停止する
        """

        if self.is_event_start():
            self.add_event_logs()
            return True
        else:
            return False
        
    def event_start(self) -> None:
        """
        description: イベントの開始について取り扱う
        -------------------
        none
        -------------------
        return: none
        """
        # DEBUG:
        print("Event Start")
        try:
            doc_ref = self.db.collection("rooms").document(self.room_id)
            doc_snapshot = doc_ref.get()
            print(doc_snapshot)
            print(doc_snapshot.to_dict())
            play_time_seconds = doc_snapshot.get("play_time_seconds")

            start_time: datetime = datetime.now()
            end_time: datetime = start_time + timedelta(minutes=play_time_seconds)
            # COMMENT: プレイ時間を超えた場合、強制的にDBの監視を停止する
            while end_time > datetime.now():
                is_finish: bool = self.check_db()
                is_game_continue: bool = self.is_game_continue()
                if is_finish:  # COMMENT: eventが発令されたらループを抜ける
                    print("Event is started")
                    break
                if not is_game_continue: # COMMENT: ゲーム自体が終了した場合、ループから抜ける
                    print("The game in this room is over")
                    break
                time.sleep(60)  # COMMENT: 60秒置きに実行
        except Exception as e:
            print(f"An error occurred in event_start: {str(e)}")
    
