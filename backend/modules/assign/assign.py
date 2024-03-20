import math
import random


class Assign:
    """
    Assign: Class -> プレイヤー割り当て管理全体を統括するクラス
    """

    def __init__(self, db, room_id: str) -> None:
        self.db = db
        self.room_id: str = room_id
        self.users_ref = None
        self.rooms_ref = None
        self.cop_ration: int = 0
        self.robber_ration: int = 0

    def set(self) -> None:
        """
        description: クラス内で共有して使用する変数の初期化
        -----------------
        none
        -----------------
        return none
        """

        self.users_ref = self.db.collection("users")
        self.rooms_ref = self.db.collection("rooms")
    
    def pick_out_cop_number(self) -> None:
        """
        description: 警察と泥棒の人数を取得する
        -----------------
        none
        -----------------
        return none
        """

        room_ref = self.rooms_ref.document(self.room_id)
        doc_snapshot = room_ref.get()
        self.cop_ration: int = doc_snapshot.get("cop_num")
        self.robber_ration: int = doc_snapshot.get("robber_num")

    def calculate_cop_number(self, users_num) -> int:
        """
        description: 警察に入れるべき人数の計算を行う
        -----------------
        users_num: int -> プレイヤーの人数
        -----------------
        return cop_num: int -> 警察の人数
        """

        cop_num: int = math.floor(
            (self.cop_ration / (self.cop_ration + self.robber_ration)) * users_num
        )
        return cop_num

    def get_users_list(self) -> list:
        """
        description: プレイヤーリストの取得
        -----------------
        none
        -----------------
        return users_list: list -> シャッフル後のプレイヤーリスト
        """

        users = self.users_ref.where("room_id", "==", self.room_id).stream()
        users_list = list(users)
        random.shuffle(users_list)  # COMMENT: userをシャッフルする
        return users_list

    def assign_member(self) -> None:
        """
        description: プレイヤーを警察・泥棒に割り当てる処理
        -----------------
        none
        -----------------
        return none
        """

        self.set()
        self.pick_out_cop_number()
        users_list: list = self.get_users_list()
        users_num: int = len(users_list)
        cop_num: int = self.calculate_cop_number(users_num)

        for user in users_list:
            user_ref = self.users_ref.document(user.id)
            if cop_num > 0:
                user_ref.update({"is_cop": True})
                cop_num -= 1
            else:
                user_ref.update({"is_cop": False})
                user_ref.update({"is_under_arrest": False})
