import json
import openai
from dotenv import load_dotenv
import os
from tabulate import tabulate  # テーブル形式表示のためにインポート

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

# パーツ情報をテーブル形式で表示
def show_parts():
    parts = load_json()
    if not parts:
        print("パーツ情報が登録されていません。")
    else:
        table = [[idx + 1, part['part_name'], part['part_value']] for idx, part in enumerate(parts)]
        print(tabulate(table, headers=["#", "Part Name", "Details"], tablefmt="grid"))

# OpenAI APIを使ってアドバイスを生成
def generate_advice(user_question, messages):
    parts = load_json()
    if not parts:
        return "パーツ情報が登録されていません。"

    parts_text = "\n".join([f"{part['part_name']}: {part['part_value']}" for part in parts])

    # ユーザーメッセージを履歴に追加
    messages.append({"role": "user", "content": f"PCパーツ情報:\n{parts_text}\n\n質問: {user_question}"})

    # トークン数計算で動的に最大値を調整
    max_allowed_tokens = 4096  # gpt-4o の最大トークン
    used_tokens = sum(len(message['content']) for message in messages)
    max_tokens = max(1000, max_allowed_tokens - used_tokens - 500)  # 最小値を1000トークンに設定

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        # 使用されたモデルを表示
        print(f"\n使用モデル: {response['model']}")

        # トークン数の表示
        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]
        total_tokens = response["usage"]["total_tokens"]
        print(f"今回使用したトークン数: {total_tokens} (入力: {prompt_tokens}, 出力: {completion_tokens})")

        # アシスタントの応答を履歴に追加
        assistant_reply = response["choices"][0]["message"]["content"].strip()
        messages.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
    except openai.error.RateLimitError:
        return "APIのクォータを超えたか、一時的に制限されています。少し時間を置いて再試行してください。"
    except openai.error.AuthenticationError:
        return "APIキーが無効です。正しいキーを設定してください。"
    except Exception as e:
        return f"予期しないエラーが発生しました: {str(e)}"

# メインプログラム
if __name__ == "__main__":
    # 会話履歴を初期化
    messages = [{"role": "system", "content": "You are a helpful assistant with expertise in computer hardware."}]

    while True:
        print("\n1. パーツ情報を追加")
        print("2. パーツ情報を表示")
        print("3. GPTにアドバイスをもらう")
        print("4. 会話履歴を表示")
        print("5. 終了")
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
            advice = generate_advice(user_question, messages)
            print(f"GPTからのアドバイス:\n{advice}")
        elif choice == "4":
            print("\n会話履歴:")
            for message in messages:
                print(f"{message['role'].capitalize()}: {message['content']}")
        elif choice == "5":
            print("終了します。")
            break
        else:
            print("無効な選択肢です。")