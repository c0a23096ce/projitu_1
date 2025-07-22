#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector
import http.cookies
import os
import html
import sys
import traceback
import cgi  # 追加
from utils import get_connection, require_login

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

    # セッション認証
    user_id = require_login()
    
    # クエリパラメータを取得（追加）
    form = cgi.FieldStorage()
    current_title = form.getfirst('title', '')

    # データベース接続
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # すべての動画を取得（新しい順）
    cursor.execute("SELECT id, title, file_path FROM videos ORDER BY upload_at DESC")
    videos = cursor.fetchall()

    print(f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <title>KouTube - トップページ</title>
      <link rel="stylesheet" href="../static/video_top.css">
    </head>
    <body>

    <header class="header">
      <div class="header-content">
        <a href="#" class="logo">
          <div class="logo-icon">VT</div>
          <div class="logo-text">KouTube</div>
        </a>
        <div class="search-container">
          <form class="search-form" method="get" action="video_search.cgi">
            <input type="text" name="title" value="{current_title}" class="search-input" placeholder="動画、チャンネル、クリエイターを検索...">
            <button type="submit" class="search-btn">🔍</button>
          </form>
          <button class="voice-search" onclick="startVoiceSearch()">🎤</button>
        </div>
        <div class="header-right">
          <a href="upload.cgi">管理👤</a>
        </div>
      </div>
    </header>      

    <div class="video-grid">
    """)

# 各動画カードを出力
    for v in videos:
        print(f"""
      <div class="video-card">
        <a href="video_view.cgi?video_id={v['id']}&user_id=1">
          <video muted>
            <source src="{v['file_path']}" type="video/mp4">
          </video>
          <div class="video-title">{v['title']}</div>
        </a>
      </div>
    """)

    print("""
    </div>
    <script src="../static/voice_search.js"></script>
    </body>
    </html>
    """)

except Exception as e:
    print_error(f"予期しないエラー: {str(e)}\n{traceback.format_exc()}")

finally:
  conn.close()
