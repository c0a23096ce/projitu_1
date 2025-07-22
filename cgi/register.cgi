#!/usr/bin/python3

import cgi
import mysql.connector
import html
import crypt
from utils import get_connection

print("Content-Type: text/html\n")

form = cgi.FieldStorage()
username = form.getvalue("username")
password = form.getvalue("password")
email = form.getvalue("email")
fname = form.getvalue("fname")
lname = form.getvalue("lname")

html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>ユーザー登録</title>
    <link rel="stylesheet" href="../static/register.css">
</head>
<body>
    <div class="auth-container">
        <h2 class="auth-title">ユーザー登録</h2>
        <p class="error-message">{message}</p>
        <form action="./register.cgi" method="post">
            <input type="text" name="username" placeholder="ユーザー名" class="auth-input" required><br>
            <input type="password" name="password" placeholder="パスワード" class="auth-input" required><br>
            <input type="email" name="email" placeholder="メールアドレス" class="auth-input" required><br>
            <input type="text" name="fname" placeholder="名" class="auth-input"><br>
            <input type="text" name="lname" placeholder="姓" class="auth-input"><br>
            <button type="submit" class="auth-btn">登録する</button>
        </form>
        <div class="auth-toggle">
            すでにアカウントをお持ちですか？ <a href="./login.cgi">ログイン</a>
        </div>
    </div>
</body>
</html>
'''


db = get_connection()
cursor = db.cursor()
    

if username and password and email and fname and lname:
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    hashed_password = crypt.crypt(password, salt)
    try:
        # SQLインジェクション脆弱性あり（意図的）
        query = f"""
        INSERT INTO users (username, password, email, fname, lname)
        VALUES ('{username}', '{hashed_password}', '{email}', '{fname}', '{lname}')
        """
        cursor.execute(query)
        db.commit()
        
        print("""
              Content-Type: text/html; charset=utf-8\n
              
              <script>
                alert('register success');
                window.location.href = './login.cgi';
              </script>
              """)

    except Exception as e:
        message = f"エラーが発生しました: {str(e)}"

    print(html_template.format(message=message))

else:
    print(html_template.format(message=""))
