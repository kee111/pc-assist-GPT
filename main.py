import json
import openai
from dotenv import load_dotenv  # dotenvをインポート
import os  # osモジュールをインポート

# .envファイルを読み込む
load_dotenv("apikey.env")

# 環境変数からAPIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# JSONファイルのパス
JSON_FILE = "pc_parts.json"

# JSONファイルからパーツ情報を読み込む
def load_json():
    try:
        with open(JSON_FILE, "r") as file:
            data = json.load(file)
            return data.get("pc_parts", [])  # "pc_parts" キーを直接取得
    except FileNotFoundError:
        return []  # ファイルが存在しない場合は空のリストを返す

# JSONファイルにデータを書き込む
def save_json(parts):
    with open(JSON_FILE, "w") as file:
        json.dump({"pc_parts": parts}, file, indent=4)

# パーツ情報を追加
def add_part(part_name, part_value):
    parts = load_json()
    parts.append({"part_name": part_name, "part_value": part_value})
    save_json(parts)
    print(f"{part_name} を {part_value} として追加しました。")

# パーツ情報を表示
def show_parts():
    parts = load_json()
    if not parts:
        print("パーツ情報が登録されていません。")
    else:
        print("登録されているパーツ情報:")
        for idx, part in enumerate(parts, start=1):
            print(f"{idx}. {part['part_name']}: {part['part_value']}")

# OpenAI APIを使ってアドバイスを生成
# OpenAI APIを使ってアドバイスを生成
def generate_advice(user_question):
    parts = load_json()
    if not parts:
        return "パーツ情報が登録されていません。"

    # パーツ情報をテキスト化
    parts_text = "\n".join([f"{part['part_name']}: {part['part_value']}" for part in parts])

    # GPTに渡すプロンプト
    prompt = f"""
    以下は現在登録されているPCパーツ情報です。この情報をもとに、以下の質問に答えてください:
    PCパーツ情報:
    {parts_text}

    質問: {user_question}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with expertise in computer hardware."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.RateLimitError:
        return "APIのクォータを超えたか、一時的に制限されています。少し時間を置いて再試行してください。"
    except Exception as e:
        return f"予期しないエラーが発生しました: {str(e)}"

# メインプログラム
if __name__ == "__main__":
    while True:
        print("\n1. パーツ情報を追加")
        print("2. パーツ情報を表示")
        print("3. GPTにアドバイスをもらう")
        print("4. 終了")
        choice = input("選択肢を入力してください: ")

        if choice == "1":
            part_name = input("パーツ名を入力してください (例: cpu, gpu): ")
            part_value = input("パーツの詳細を入力してください (例: Intel Core i7-13700K): ")
            add_part(part_name, part_value)
        elif choice == "2":
            show_parts()
        elif choice == "3":
            user_question = input("質問を入力してください (例: マザーボードの最新バージョンを確認して): ")
            print("GPTからのアドバイスを生成中...")
            advice = generate_advice(user_question)
            print(f"GPTからのアドバイス:\n{advice}")
        elif choice == "4":
            print("終了します。")
            break
        else:
            print("無効な選択肢です。");print(f"使用しているAPIキー: {openai.api_key[:10]}********")