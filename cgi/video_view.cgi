#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi
import mysql.connector
import html
import sys
import traceback
from utils import get_connection, require_login
import random

# エラーをブラウザに表示するための設定
def print_error(error_msg):
    print("Content-Type: text/html; charset=UTF-8")
    print()
    print(f"""
    <html>
    <head><title>エラー</title></head>
    <body>
        <h1>エラーが発生しました</h1>
        <pre>{str(error_msg)}</pre>
        <a href='login.cgi'>ログインページへ</a>
    </body>
    </html>
    """)

try:
    print("Content-Type: text/html; charset=UTF-8")
    print()

    # セッション認証（utils.pyのrequire_login関数を使用）
    user_id = require_login()

    form = cgi.FieldStorage()
    video_id = form.getfirst("video_id", "1")
    current_title = form.getfirst('title', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 動画情報取得
    cursor.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
    video = cursor.fetchone()
    if not video:
        print("<h1>動画が見つかりません</h1>")
        exit()

    # コメント投稿処理
    if "content" in form and user_id:
        content = form.getfirst("content", "")
        cursor.execute(
            "INSERT INTO comments (video_id, user_id, content) VALUES (%s, %s, %s)",
            (video_id, user_id, content)
        )
        conn.commit()

    # 👍 いいね処理（トグル式）
    if form.getfirst("like") == "1" and user_id:
        # 既にいいねしているか確認
        cursor.execute(
            "SELECT * FROM likes WHERE video_id = %s AND user_id = %s",
            (video_id, user_id)
        )
        if cursor.fetchone():
            # 既にいいねしていれば削除（取り消し）
            cursor.execute(
                "DELETE FROM likes WHERE video_id = %s AND user_id = %s",
                (video_id, user_id)
            )
        else:
            # いいねしていなければ追加
            cursor.execute(
                "INSERT INTO likes (video_id, user_id) VALUES (%s, %s)",
                (video_id, user_id)
            )
            # 低評価があれば消す
            cursor.execute(
                "DELETE FROM dislikes WHERE video_id = %s AND user_id = %s",
                (video_id, user_id)
            )
        conn.commit()

    # 👎 低評価処理（トグル式）
    if form.getfirst("dislike") == "1" and user_id:
        cursor.execute(
            "SELECT * FROM dislikes WHERE video_id = %s AND user_id = %s",
            (video_id, user_id)
        )
        if cursor.fetchone():
            # 既に低評価していれば削除（取り消し）
            cursor.execute(
                "DELETE FROM dislikes WHERE video_id = %s AND user_id = %s",
                (video_id, user_id)
            )
        else:
            # 低評価していなければ追加
            cursor.execute(
                "INSERT INTO dislikes (video_id, user_id) VALUES (%s, %s)",
                (video_id, user_id)
            )
            # いいねがあれば消す
            cursor.execute(
                "DELETE FROM likes WHERE video_id = %s AND user_id = %s",
                (video_id, user_id)
            )
        conn.commit()

    # 👍 いいね数取得
    cursor.execute("SELECT COUNT(*) AS cnt FROM likes WHERE video_id = %s", (video_id,))
    likes = cursor.fetchone()["cnt"]

    # 👎 低評価数取得
    cursor.execute("SELECT COUNT(*) AS cnt FROM dislikes WHERE video_id = %s", (video_id,))
    dislikes = cursor.fetchone()["cnt"]

    # コメント一覧取得
    cursor.execute("""
        SELECT comments.content, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.video_id = %s
        ORDER BY comments.wrote_at DESC
    """, (video_id,))
    comments = cursor.fetchall()

    # おすすめ動画全部取得（自分以外）
    cursor.execute("""
        SELECT id, title, file_path
        FROM videos
        WHERE id != %s
    """, (video_id,))
    all_recommendations = cursor.fetchall()

    # その中からランダムに3つ選ぶ
    recommendations = random.sample(all_recommendations, k=min(3, len(all_recommendations)))

    # HTML出力開始
    print(f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{video['title']}</title>
        <link rel="stylesheet" href="../static/video_view.css">
        <link rel="stylesheet" href="../static/header.css">
        <link rel="stylesheet" href="../static/background.css">
        <script src="../static/header.js" defer></script>
    </head>
    <body>
    <!-- ヘッダー部分は既存のまま -->
    <header class="header">
        <div class="header-content">
        <a href="video_top.cgi" class="logo">
            <div class="logo-icon">VT
            </div>
            <div class="logo-text">KouTube
            </div>
        </a>
        <div class="search-container">
        <form class="search-form" method="get" action="video_search.cgi">
            <input type="text" name="title" value="{current_title}" class="search-input" placeholder="動画を検索...">
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
        
        <div class="main-container">
            <div class="main-content">
                <div class="video-container">
                    <video controls>
                        <source src="{video['file_path']}" type="video/mp4">
                    </video>
                </div>
                
                <div class="video-info">
                    <h1>{video['title']}</h1>
                    <div class="video-description">{video['description']}</div>
                    
                    <div class="like-form">
                        <form method="get" action="video_view.cgi">
                            <input type="hidden" name="video_id" value="{video_id}">
                            <input type="hidden" name="like" value="1">
                            <input type="submit" value="👍 {likes}">
                        </form>
                        <form method="get" action="video_view.cgi">
                            <input type="hidden" name="video_id" value="{video_id}">
                            <input type="hidden" name="dislike" value="1">
                            <input type="submit" value="👎 {dislikes}">
                        </form>
                    </div>
                </div>
                
                <div class="comment-section">
                    <h2>コメント</h2>
    """)

    for c in comments:
        print(f"""
            <div class="comment-box">
                <div class="comment-username">{c['username']}</div>
                <div class="comment-content">{c['content']}</div>
            </div>
        """)

    print(f"""
                <div class="comment-form">
                    <h3>コメントを投稿</h3>
                    <form method="post" action="video_view.cgi">
                        <input type="hidden" name="video_id" value="{video_id}">
                        <textarea name="content" placeholder="コメントを追加..."></textarea>
                        <br>
                        <input type="submit" class="comment-btn" value="コメント">
                    </form>
                </div>
            </div>
        </div>
        
        <div class="sidebar">
            <h2>次の動画</h2>
            <div class="recommend-list">
    """)

    for r in recommendations:
        print(f"""
        <div class="recommend-item">
            <video muted>
                <source src="{r['file_path']}" type="video/mp4">
            </video>
            <div class="recommend-item-info">
                <a href="video_view.cgi?video_id={r['id']}">{r['title']}</a>
                <div class="recommend-item-meta">おすすめ</div>
            </div>
        </div>
    """)

    print("""
            </div>
        </div>
    </div>
</div>
</body>
</html>
""")

    cursor.close()
    conn.close()

except Exception as e:
    print_error(f"予期しないエラー: {str(e)}\n{traceback.format_exc()}")
