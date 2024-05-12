import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore


class DB:
    """
    DB: Class -> firebaseのDBを統括するクラス
    """
    def __init__(self) -> None:
        pass

    def connection(self):
        """
        description: firebaseのDB初期化
        -------------------
        none
        -------------------
        return: db
        """

        #.envファイルから環境変数を読み込む
        load_dotenv()

        #環境変数からFirebaseの秘密鍵ファイルのパスを取得
        firebase_key = os.getenv("FIREBASE_KEY_PATH")
        program_directory = os.path.dirname(os.path.abspath(__file__))
        firebase_key_path = program_directory + "/" + firebase_key

        #Firebase初期化
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        return db