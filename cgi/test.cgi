#!/usr/bin/python3

import cgi, crypt, mysql.connector, random, string, os

form = cgi.FieldStorage()
print("Content-Type: text/html") 

print()                           # ← ヘッダーとHTML本体の間に空行が必要

print("<html><body>")
print("<h1>Hello, world!</h1>")
print("</body></html>")
