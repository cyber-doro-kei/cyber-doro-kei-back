from pydantic import BaseModel

class StartTimer(BaseModel):
    is_admin: bool
# test用クラス
class Item(BaseModel):
    test_message: str