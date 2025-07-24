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
            <link rel="stylesheet" href="../static/video_search.css">
            <link rel="stylesheet" href="../static/header.css">
            <link rel="stylesheet" href="../static/background.css">
            <script src="../static/header.js" defer></script>
        </head>
        <body>
            <header class="header">
                <div class="header-content">
                    <a href="video_top.cgi" class="logo">
                        <div class="logo-icon">VT</div>
                        <div class="logo-text">KouTube</div>
                    </a>
                    <div class="search-container">
                        <form class="search-form" method="get" action="video_search.cgi">
                            <input type="text" name="title" value="{title}" class="search-input" placeholder="動画を検索...">
                            <button type="submit" class="search-btn">🔍</button>
                        </form>
                        <button class="voice-search" onclick="startVoiceSearch()">🎤</button>
                    </div>
                    <div class="header-right">
                        <div class="dropdown">
                            <button id="adminMenuBtn" class="dropbtn">管理👤</button>
                            <div id="adminMenu" class="dropdown-content">
                                <a href="upload.cgi">動画アップロード</a>
                                <a href="logout.cgi">ログアウト</a>
                            </div>
                        </div>
                    </div>
                </div>
            </header>
            <div class="mt-header">
                <div class="result-area">
                    <h2>検索結果</h2>
                    <ul class="result-list">
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
                <video controls src="{file_path}" width="240"></video><br>
                タイトル: {video_title}<br>
                </a>
            </li>
            """)
    else:
        print('<li class="no-result">該当する動画はありません。</li>')
    print("""
        </ul>
    </div>
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