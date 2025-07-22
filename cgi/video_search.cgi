#!/usr/bin/python3
import cgi
import mysql.connector
import sys
import os
from utils import get_connection, require_login
try:
    user_id = require_login()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    title = cgi.FieldStorage().getfirst('title', '').strip()
    
    query = f"SELECT * FROM videos WHERE title LIKE '%{title}%' ORDER BY upload_at DESC"
    cursor.execute(query)
    
    results = cursor.fetchall()
    
    print("Content-Type: text/html; charset=utf-8")
    print()
    print("""
    <html>
    <head>
        <title>動画検索</title>
    </head>
    <body>
        <h1>動画検索</h1>
        <form method="get" action="video_search.cgi">
            <input type="text" name="title" value="{title}" placeholder="動画タイトルを入力">
            <input type="submit" value="検索">
        </form>
        <h2>検索結果</h2>
        <ul>
    """.format(title=title))
    # print(f"use_query: {query}<br>")
    if results:
        for row in results:
            video_id = row['id']
            video_title = row['title']
            file_path = row['file_path']
            print(f"""
            <li>
                <a href="video_view.cgi?video_id={video_id}&user_id={user_id}">
                <video controls src="/project/projitu_1/videos/{file_path}" width="240"></video><br>
                タイトル: {video_title}<br>
                </a>
            </li>
            """)
    else:
        print("<li>該当する動画はありません。</li>")
    print("""
        </ul>
        <a href="video_top.cgi">動画一覧に戻る</a>
    </body>
    </html>
    """)

except mysql.connector.Error as e:
    print("Content-Type: text/html; charset=utf-8")
    print()
    # print(f"use_query: {query}<br>")
    print(f"<p style='color:red'>予期せぬエラーが発生しました: {str(e)}</p>")

finally:
    conn.close()

# テストインジェクション
# ' UNION SELECT id, '', password, '', email, 0, NOW() FROM users -- ' 