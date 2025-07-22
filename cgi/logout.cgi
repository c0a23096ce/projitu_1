#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cgi
import os

print("Content-Type: text/html; charset=UTF-8")
# セッション情報（例: クッキー）を削除
print("Set-Cookie: session_id=deleted; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/")
print()
print("""
<html>
<head><meta http-equiv="refresh" content="1;url=login.cgi"></head>
<body>
  <h1>ログアウトしました</h1>
  <a href="login.cgi">ログインページへ</a>
</body>
</html>
""")