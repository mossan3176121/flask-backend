import os
import sqlite3
import csv

DATABASE_PATH = "audio_files.db"
TABLE_NAME = "audio_files"
PHRASE_PATH = r"C:\main\EnglishApp\DictaionApp\myenv\phrase\PHaVE\PHaVE.csv"

# データベースのセットアップ
def setup_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            id INT,
            verb TEXT,
            verb_jp TEXT,
            sentence TEXT,
            sentence_jp,
            path TEXT
        )
    """.format(TABLE_NAME))
    conn.commit()
    conn.close()
# データベースにcsvファイルに書き込まれたデータの追加
def add_database():
    # SQLite データベースに接続
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    with open(PHRASE_PATH, "r", encoding= "utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            cursor.execute("""
                INSERT OR IGNORE INTO {} (id, verb, verb_jp, sentence, sentence_jp, path)
                VALUES (?, ?, ?, ?, ?, ?)
            """.format(TABLE_NAME), row)

    print("差分データを追加しました。")
    conn.commit()
    conn.close()
# データベースの読み込み

# データベースの削除
def delete_db():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print(f"{DATABASE_PATH}を削除しました")
    else:
        print("データベースが見つかりません")
    
def read_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM {}".format(TABLE_NAME))
    rows = cursor.fetchall()
    print("===== データベースの内容 =====")
    for row in rows:
        print(row)
        # print(f"id {row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]}, {row[5]}")
    conn.close()


if __name__ == "__main__":
    delete_db()
    setup_database()
    add_database()
    read_db()

