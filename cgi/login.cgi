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
from utils import get_connection

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
    <link rel="stylesheet" href="../static/register.css">
</head>
<body>
    <div class="auth-container">
        <h2 class="auth-title">ログイン</h2>
        <p class="error-message">{message}</p>
        <form action="./login.cgi" method="post">
            <input type="email" name="email" placeholder="メールアドレス" class="auth-input" required><br>
            <input type="password" name="password" placeholder="パスワード" class="auth-input" required><br>
            <button type="submit" class="auth-btn">ログイン</button>
        </form>
        <div class="auth-toggle">
            アカウントをお持ちでない方は <a href="./register.cgi">新規登録</a>
        </div>
    </div>
</body>
</html>
'''


# DB接続
print("Content-Type: text/html; charset=utf-8")

db = get_connection()
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
                query = (
                    f"INSERT INTO sessions (session_id, user_id, expires_at) "
                    f"VALUES ('{new_session_id}', '{user_data[0]}', '{EXPIRES_DATETIME}') "
                    f"ON DUPLICATE KEY UPDATE session_id='{new_session_id}', expires_at='{EXPIRES_DATETIME}'"
                )
                # print(f"Executing query: {query}")  # デバッグ用
                cursor.execute(query)
                db.commit()
                
                cookie_datetime = datetime.datetime.fromtimestamp(EXPIRES_TIME).strftime('%a, %d %b %Y %H:%M:%S GMT')
                cookie_obj = http.cookies.SimpleCookie()
                cookie_obj["session_id"] = new_session_id
                cookie_obj["session_id"]["expires"] = cookie_datetime
                
                print(cookie_obj.output())
                print()
                
                # video_top.cgiへリダイレクト
                print("""                    
                    <script>
                    alert('ログイン成功しました。');
                    window.location.href = './video_top.cgi';
                    </script>
                    """)
                
            else:
                message = "ログイン失敗：メールアドレスまたはパスワードが違います。"
                
        else:
            message = "ログイン失敗：メールアドレスまたはパスワードが違います。"

    except Exception as e:
        message = f"エラーが発生しました: {str(e)}"

    print(html_template.format(message=message))

else:
    # 初回アクセスや空入力
    print(html_template.format(message=""))

db.close()