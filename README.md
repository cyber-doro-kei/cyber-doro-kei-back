# cyber-doro-kei-back

スマートフォン向けアプリ「Cyberドロケイ」で用いるバックエンドサーバーのプログラムです。
このアプリを遊ぶためには、このバックエンドサーバーを起動する必要があります。

## 注意点
このサーバーを一般に公開する場合は、法令上の届け出が必要な場合があります。
このプログラムの利用によって発生するいかなる損害についても、作者は一切の責任を負いません。

## 環境構築
```
$ pip3 install -r requirements.txt
```

## サーバー起動
```
python3 -m uvicorn app:app --port 8000  # specify the port you want to use
```
