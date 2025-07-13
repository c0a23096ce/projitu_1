#!/usr/bin/python3

import cgi
import mysql.connector
import html
import crypt
import http.cookies
import uuid
import os
import time
import datetime

EXPIRES_TIME = time.time() + 60 * 60  # 1時間後に期限切れ
EXPIRES_DATETIME = datetime.datetime.fromtimestamp(EXPIRES_TIME).strftime('%Y-%m-%d %H:%M:%S')

# Cookie取得
cookie = http.cookies.SimpleCookie()
if "HTTP_COOKIE" in os.environ:
    cookie.load(os.environ["HTTP_COOKIE"])

form = cgi.FieldStorage()
email = form.getvalue("email")
password = form.getvalue("password")

message = ""

html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>ログインページ</title>
</head>
<body>
    <h2>ログイン</h2>
    <form action="./login.cgi" method="post">
        メールアドレス: <input type="text" name="email"><br>
        パスワード: <input type="password" name="password"><br>
        <input type="submit" value="ログイン">
    </form>
    <p><a href="./register.cgi">新規登録はこちら</a></p>
    <p>{message}</p>
</body>
</html>
'''

# DB接続
print("Content-Type: text/html; charset=utf-8")
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="passwordA1!",
        database="KouTube"
    )
    cursor = db.cursor()

    # ログイン処理
    if email and password:
        try:
            # SQLインジェクション脆弱性あり
            query = f"SELECT * FROM users WHERE email = '{email}'"
            # print(f"Executing query: {query}")  # デバッグ用
            cursor.execute(query)
            user_data = cursor.fetchone()
            if user_data:
                stored_password = user_data[2]
                salt = "$".join(stored_password.split("$")[:3])
                hashed_password = crypt.crypt(password, salt)
                if hashed_password == stored_password:
                    # セッションID発行
                    new_session_id = str(uuid.uuid4())
                    # SQLインジェクション脆弱性あり
                    query = f"INSERT INTO sessions (session_id, user_id, expires_at) VALUES ('{new_session_id}', '{user_data[0]}', '{EXPIRES_DATETIME}')"
                    # print(f"Executing query: {query}")  # デバッグ用
                    cursor.execute(query)
                    db.commit()
                    
                    cookie_datetime = datetime.datetime.fromtimestamp(EXPIRES_TIME).strftime('%a, %d %b %Y %H:%M:%S GMT')
                    cookie_obj = http.cookies.SimpleCookie()
                    cookie_obj["session_id"] = new_session_id
                    cookie_obj["session_id"]["expires"] = cookie_datetime
                    
                    print(cookie_obj.output())
                    
                    
                    # print("""
                    #   Content-Type: text/html; charset=utf-8\n
                      
                    #   <script>
                    #     alert('ログイン成功しました。');
                    #     window.location.href = './index.cgi';
                    #   </script>
                    #   """)
                    # index.cgiへリダイレクト
                    
                else:
                    message = "ログイン失敗：メールアドレスまたはパスワードが違います。"
                    
            else:
                message = "ログイン失敗：メールアドレスまたはパスワードが違います。"

        except Exception as e:
            message = f"エラーが発生しました: {html.escape(str(e))}"

        print()
        print(html_template.format(message=message))

    else:
        # 初回アクセスや空入力
        print()
        print(html_template.format(message="メールアドレスとパスワードを入力してください。"))

except Exception as e:
    print()
    print(html_template.format(message="データベース接続失敗: " + html.escape(str(e))))
    exit()

finally:
    try:
        db.close()
    except:
        pass  # DB接続が失敗している場合は無視