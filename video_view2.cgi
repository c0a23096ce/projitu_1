#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi
import mysql.connector
from db_connect import get_connection

print("Content-Type: text/html; charset=UTF-8")
print()

form = cgi.FieldStorage()
video_id = form.getfirst("video_id", "1")
user_id = "2"  # ★ このファイルは2人目ユーザー用

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# 動画取得
cursor.execute("SELECT * FROM videos WHERE id = %s", (video_id,))
video = cursor.fetchone()
if not video:
    print("<h1>動画が見つかりません</h1>")
    exit()

# コメント投稿
if "content" in form:
    content = form.getfirst("content", "")
    cursor.execute(
        "INSERT INTO comments (video_id, user_id, content) VALUES (%s, %s, %s)",
        (video_id, user_id, content)
    )
    conn.commit()

# 👍 高評価処理
if form.getfirst("like") == "1":
    try:
        cursor.execute(
            "INSERT INTO likes (video_id, user_id) VALUES (%s, %s)",
            (video_id, user_id)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        pass

# 👎 低評価処理
if form.getfirst("dislike") == "1":
    try:
        cursor.execute(
            "INSERT INTO dislikes (video_id, user_id) VALUES (%s, %s)",
            (video_id, user_id)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        pass

# 高評価数取得
cursor.execute("SELECT COUNT(*) AS cnt FROM likes WHERE video_id = %s", (video_id,))
likes = cursor.fetchone()["cnt"]

# 低評価数取得
cursor.execute("SELECT COUNT(*) AS cnt FROM dislikes WHERE video_id = %s", (video_id,))
dislikes = cursor.fetchone()["cnt"]

# コメント取得
cursor.execute("""
    SELECT comments.content, users.username
    FROM comments
    JOIN users ON comments.user_id = users.id
    WHERE comments.video_id = %s
    ORDER BY comments.wrote_at DESC
""", (video_id,))
comments = cursor.fetchall()

# おすすめ動画取得
cursor.execute("""
    SELECT id, title, file_path
    FROM videos
    WHERE id != %s
    ORDER BY upload_at DESC
    LIMIT 2
""", (video_id,))
recommendations = cursor.fetchall()

# HTML表示
print(f"""
<html>
<head>
  <meta charset="UTF-8">
  <title>{video['title']}</title>
</head>
<body>
<h1>{video['title']}</h1>
<p>{video['description']}</p>
<video controls>
  <source src="{video['file_path']}" type="video/mp4">
</video>

<!-- 👍👎 -->
<div>
  <form method="get" action="video_view2.cgi" style="display:inline;">
    <input type="hidden" name="video_id" value="{video_id}">
    <input type="hidden" name="like" value="1">
    <input type="submit" value="👍 いいね ({likes})">
  </form>
  <form method="get" action="video_view2.cgi" style="display:inline;">
    <input type="hidden" name="video_id" value="{video_id}">
    <input type="hidden" name="dislike" value="1">
    <input type="submit" value="👎 低評価 ({dislikes})">
  </form>
</div>

<!-- おすすめ動画 -->
<h2>おすすめ動画</h2>
<div>
""")

for r in recommendations:
    print(f"""
    <div style="margin-bottom: 10px;">
      <video muted width="200">
        <source src="{r['file_path']}" type="video/mp4">
      </video><br>
      <a href="video_view2.cgi?video_id={r['id']}">{r['title']}</a>
    </div>
    """)

print("</div>")

# コメント表示
print("<h2>コメント</h2>")
for c in comments:
    print(f"<p><strong>{c['username']}:</strong> {c['content']}</p>")

# コメント投稿フォーム
print(f"""
<form method="post" action="video_view2.cgi">
  <input type="hidden" name="video_id" value="{video_id}">
  <textarea name="content" rows="4" cols="60" placeholder="コメントを入力してください"></textarea><br>
  <input type="submit" value="コメントを投稿">
</form>
</body>
</html>
""")

cursor.close()
conn.close()
