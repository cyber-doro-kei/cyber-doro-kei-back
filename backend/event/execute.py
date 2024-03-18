import os
import sys

from event import Event

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import DB

# COMMENT: Firebase初期化
db_init = DB()
db = db_init.connection()

room_id = sys.argv[1]
event = Event(db, room_id)
event.main()