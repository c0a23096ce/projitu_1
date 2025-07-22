#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cgi
import os
from utils import get_connection, require_login
import http.cookies

user_id = require_login()
# セッションの削除
if user_id:
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        query = f"DELETE FROM sessions WHERE user_id = '{user_id}'"
        cursor.execute(query)
        conn.commit()

# Cookieの削除
cookie = http.cookies.SimpleCookie()
cookie["session_id"] = ""
cookie["session_id"]["max-age"] = 0
cookie["session_id"]["path"] = "/"

print("Content-Type: text/html; charset=UTF-8")
print(cookie.output())
print("""
<html>
<head>
  <meta http-equiv="refresh" content="1;url=login.cgi">
  <link rel="stylesheet" href="../static/logout.css">
  <title>ログアウト</title>
</head>
<body>
  <div class="logout-container">
    <div class="logout-title">ログアウトしました</div>
    <div class="logout-message">ご利用ありがとうございました。</div>
    <a href="login.cgi" class="logout-link">ログインページへ</a>
  </div>
</body>
</html>
""")