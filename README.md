# cyber-doro-kei-back

## 起動方法
1. docker compose build
2. docker compose up -d
3. http://localhost:8000にアクセス

### dicker内のbashを触る
1. docker ps でコンテナidを入手
2. docker exec -it <コンテナID> bash
3. uvicorn app:app --reload --host 0.0.0.0 --port 8000 で何が原因で上手くいってないかわかるuvicorn app:app --reload --host 0.0.0.0 --port 8000 