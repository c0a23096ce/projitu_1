#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi
import mysql.connector
from db_connect import get_connection
import random

print("Content-Type: text/html; charset=UTF-8")
print()

form = cgi.FieldStorage()
video_id = form.getfirst("video_id", "1")
user_id = form.getfirst("user_id", "1")

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

# 👍 いいね処理
if form.getfirst("like") == "1" and user_id:
    try:
        cursor.execute(
            "INSERT INTO likes (video_id, user_id) VALUES (%s, %s)",
            (video_id, user_id)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        pass

# 👎 低評価処理
if form.getfirst("dislike") == "1" and user_id:
    try:
        cursor.execute(
            "INSERT INTO dislikes (video_id, user_id) VALUES (%s, %s)",
            (video_id, user_id)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        pass

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
  <style>
    body {{
        font-family: sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: #f9f9f9;
    }}
    h1 {{
        font-size: 24px;
    }}
    video {{
        width: 100%;
        margin-bottom: 20px;
    }}
    .like-form {{
        margin-bottom: 30px;
    }}
    .like-form form {{
        display: inline;
    }}
    .like-form input[type=submit] {{
        margin-right: 10px;
        padding: 6px 16px;
        border: none;
        border-radius: 4px;
        background-color: #ddd;
        cursor: pointer;
    }}
    .recommend-section {{
        margin-bottom: 40px;
    }}
    .recommend-list {{
        display: flex;
        gap: 20px;
        justify-content: space-between;
    }}
    .recommend-item {{
        flex: 1 1 0;
        max-width: 32%;
        background: #fff;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        text-align: center;
    }}
    .recommend-item video {{
        width: 100%;
        height: auto;
    }}
    .recommend-item a {{
        display: block;
        margin-top: 8px;
        font-weight: bold;
        color: #333;
        text-decoration: none;
    }}
    .comment-section {{
        background: #fff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 5px #ccc;
    }}
    .comment-box {{
        border-bottom: 1px solid #ddd;
        padding: 10px 0;
    }}
    .comment-username {{
        font-weight: bold;
    }}
    .comment-content {{
        white-space: pre-wrap;
    }}
    .comment-form {{
        margin-top: 20px;
    }}
    textarea {{
        width: 100%;
        height: 80px;
        resize: vertical;
        font-size: 14px;
    }}
    input[type=submit].comment-btn {{
        margin-top: 10px;
        padding: 6px 16px;
        background-color: #e62117;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }}
    input[type=submit].comment-btn:hover {{
        background-color: #cc1c13;
    }}
  </style>
</head>
<body>

<h1>{video['title']}</h1>
<p>{video['description']}</p>
<video controls>
  <source src="{video['file_path']}" type="video/mp4">
</video>

<!-- 👍👎 いいね・低評価 -->
<div class="like-form">
  <form method="get" action="video_view.cgi">
    <input type="hidden" name="video_id" value="{video_id}">
    <input type="hidden" name="user_id" value="{user_id}">
    <input type="hidden" name="like" value="1">
    <input type="submit" value="👍 いいね ({likes})">
  </form>
  <form method="get" action="video_view.cgi">
    <input type="hidden" name="video_id" value="{video_id}">
    <input type="hidden" name="user_id" value="{user_id}">
    <input type="hidden" name="dislike" value="1">
    <input type="submit" value="👎 低評価 ({dislikes})">
  </form>
</div>

<!-- 🎯 おすすめ動画 -->
<div class="recommend-section">
  <h2>おすすめの動画</h2>
  <div class="recommend-list">
""")

for r in recommendations:
    print(f"""
    <div class="recommend-item">
      <video muted>
        <source src="{r['file_path']}" type="video/mp4">
      </video>
      <a href="video_view.cgi?video_id={r['id']}&user_id={user_id}">{r['title']}</a>
    </div>
    """)

print("</div></div>")

print(f"""
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
      <input type="hidden" name="user_id" value="{user_id}">
      <textarea name="content" placeholder="コメントを入力..."></textarea><br>
      <input type="submit" class="comment-btn" value="コメントを投稿">
    </form>
  </div>
</div>

</body>
</html>
""")

cursor.close()
conn.close()
