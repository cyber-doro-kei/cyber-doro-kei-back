import time
from datetime import datetime, timedelta
import random
from google.cloud.firestore import FieldFilter
from google.cloud import firestore

class Event:
    """
    Event: Class -> イベント全体を統括するクラス
    """

    def __init__(self, db, room_id: str) -> None:
        self.db = db
        self.room_id: str = room_id
        self.robber_num = 0
        self.event_target_robber_name: str = ""

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
            is_under_arrest: bool = user_snapshot.get("is_under_arrest")
            if is_under_arrest:
                arrest_num += 1
        if (
            self.robber_num // 2 <= arrest_num
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
            "created_at": firestore.SERVER_TIMESTAMP,
            "text": "テストイベント"
        }
        event_logs_ref = self.db.collection("event_logs").document(self.room_id).collection("logs").document()
        event_logs_ref.set(data)

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
        try:
            doc_ref = self.db.collection("rooms").document(self.room_id)
            doc_snapshot = doc_ref.get()
            play_time_seconds = doc_snapshot.get("play_time_seconds")
            print(f"play_time_seconds", play_time_seconds)

            start_time: datetime = datetime.now()
            end_time: datetime = start_time + timedelta(seconds=play_time_seconds*60)
            print(f"end_time: {end_time}")
            # COMMENT: プレイ時間を超えた場合、強制的にDBの監視を停止する
            while end_time > datetime.now():
                is_finish: bool = self.check_db()
                print(f"is_finish: {is_finish}")
                is_game_continue: bool = self.is_game_continue()
                if is_finish:  # COMMENT: eventが発令されたらループを抜ける
                    target_id = self.select_event_target()
                    print(f"target_id: {target_id}")
                    if not self.check_event_clear(target_id): 
                        self.event_release()
                        print("event_release") # COMMENT: イベントが成功しなかった場合、解放処理を行う

                    break
                if not is_game_continue: # COMMENT: ゲーム自体が終了した場合、ループから抜ける
                    print("The game in this room is over")
                    break
                time.sleep(60)  # COMMENT: 60秒置きに実行
                print("60 time sleep")
            print("while finish")
        except Exception as e:
            print(f"Error {e}")
    
    def select_event_target(self) -> str:
        """
        description: ○○を捕まえろeventの○○を決める
        -------------------
        none
        -------------------
        return: str -> user_id
        """
        # COMMENT: 泥棒で捕まってない人を取得
        users_ref = self.db.collection("users")
        free_robber_users = users_ref.where(filter=FieldFilter("room_id", "==", self.room_id)).where(filter=FieldFilter("is_cop", "==" ,False)).where(filter=FieldFilter("is_under_arrest", "==" ,False)).get()
        free_robber_users_list = list(free_robber_users)
        random.shuffle(free_robber_users_list) # COMMENT : シャッフルする
        target = free_robber_users_list[0]
        # COMMENT:選ばれたユーザーのドキュメントを取得
        target_doc = users_ref.document(target.id).get()

        doc_ref = self.db.collection("users").document(target_doc.id)
        doc_snapshot = doc_ref.get()
        self.event_target_robber_name = doc_snapshot.get("name")

        event_logs_ref = self.db.collection("event_logs").document(self.room_id).collection("logs").document()
        data = {
            "created_at": firestore.SERVER_TIMESTAMP,
            "text": f'イベントが発令しました。10分以内に警察陣営が{self.event_target_robber_name}を捕まえないと牢屋の半数が解放されます。'
        }
        event_logs_ref.set(data)

        return target_doc.id
    
    def check_event_clear(self,user_id) -> bool:
        """
        description: 指定されたuser_idのドキュメントのis_under_arrestフィールドがtrueになるまで10分間監視する。
                     10分経ってもtrueにならなかった場合はFalseを返す。
        -------------------
        user_id: str -> 監視対象のユーザーID
        -------------------
        return: boolean -> イベントが成功したか否かのフラグ 
                           is_under_arrestがtrueになったらTrue、10分経ってもFalseの場合はFalse
        """
        start_time = time.time()  # COMMENT: 開始時刻を記録
        timeout = 600  # COMMENT: 10分のタイムアウト時間(秒)
        
        while True:
            users_ref = self.db.collection("users")
            target_ref = users_ref.document(user_id)
            doc_snapshot = target_ref.get()

            if doc_snapshot.exists and doc_snapshot.get("is_under_arrest"):
                event_logs_ref = self.db.collection("event_logs").document(self.room_id).collection("logs").document()
                data = {
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "text": f'{self.event_target_robber_name}が逮捕されました。イベントクリアです'
                }
                event_logs_ref.set(data)

                return True
            
            # COMMENT: 10分なにもなかったらfalseを返す
            if time.time() - start_time > timeout:
                event_logs_ref = self.db.collection("event_logs").document(self.room_id).collection("logs").document()
                data = {
                    "creted_at": firestore.SERVER_TIMESTAMP,
                    "text": f'イベント失敗です。捕まっている泥棒の半数が解放されます。'
                }
                event_logs_ref.set(data)

                break

        return False

    def event_release(self) -> None:
        """
        description: イベントが成功したとき捕まっている人の半数を解放する
        -------------------
        none
        -------------------
        return: none
        """
        # COMMENT: 泥棒で捕まってる人を取得
        users_ref = self.db.collection("users")
        arrested_users = users_ref.where("room_id", "==", self.room_id).where("is_cop", "==" ,False).where("is_under_arrest", "==", True).stream()        
        arrested_users_list = list(arrested_users)
        
        # COMMENT:解放する人数を計算
        num_to_release = len(arrested_users_list) // 2
        print(num_to_release)
        # COMMENT:シャッフル
        random.shuffle(arrested_users_list)

        # COMMENT:解放処理
        for i in range(num_to_release):
            user_doc = arrested_users_list[i]
            user_ref = users_ref.document(user_doc.id)
            event_logs_ref = self.db.collection("event_logs").document(self.room_id).collection("logs").document()
            data = {
                "created_at": firestore.SERVER_TIMESTAMP,
                "text": f'{self.event_target_robber_name}はイベント失敗により解放されました。'
            }
            event_logs_ref.set(data)
            user_ref.update({"is_under_arrest": False})
        