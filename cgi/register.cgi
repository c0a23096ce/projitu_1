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
</head>
<body>
    <h2>ユーザー登録</h2>
    <form action="./register.cgi" method="post">
        ユーザー名: <input type="text" name="username"><br>
        パスワード: <input type="password" name="password"><br>
        メールアドレス: <input type="email" name="email"><br>
        名: <input type="text" name="fname"><br>
        姓: <input type="text" name="lname"><br>
        <input type="submit" value="登録">
    </form>
    <p>{message}</p>
</body>
</html>
'''

db = get_connection()
cursor = db.cursor()
    

if username and password and email:
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
        message = f"エラーが発生しました: {html.escape(str(e))}"

    print(html_template.format(message=message))

else:
    print(html_template.format(message="すべての必須項目を入力してください。"))
