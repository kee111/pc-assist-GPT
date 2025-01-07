from dotenv import load_dotenv
import os

# .envファイルの読み込み
load_dotenv("apikey.env")

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(f"APIキーが正しく読み込まれました: {api_key[:10]}********")
else:
    print("APIキーが読み込まれていません。")