import os
import sys
from timeit import Timer
import pytz
from event import Event

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# from cyber_doro_kei_back.db import DB
from db import DB
jst = pytz.timezone("Asia/Tokyo")
# COMMENT: Firebase初期化
db_init = DB()
db = db_init.connection()
# DEBUG: コマンドライン引数を取得
print(sys.argv)
room_id = sys.argv[1]
event = Event(db, room_id)
event.event_start()
timer = Timer(db, room_id,jst)
timer.execute_timer()