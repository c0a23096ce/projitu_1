#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector
import http.cookies
import os
import html
import sys
import traceback
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
        <pre>{html.escape(str(error_msg))}</pre>
        <a href='login.cgi'>ログインページへ</a>
    </body>
    </html>
    """)

try:
    print("Content-Type: text/html; charset=UTF-8")
    print()

    # セッション認証（utils.pyのrequire_login関数を使用）
    user_id = require_login()

    # データベース接続
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # すべての動画を取得（新しい順）
    cursor.execute("SELECT id, title, file_path FROM videos ORDER BY upload_at DESC")
    videos = cursor.fetchall()

    print(f"""
    <html>
    <head>
      <meta charset="UTF-8">
      <title>動画一覧（トップ）</title>
      <style>
        body {{
          font-family: sans-serif;
          background-color: #f9f9f9;
          margin: 0;
          padding: 20px;
        }}

        h1 {{
          text-align: center;
          color: #333;
        }}

        .video-grid {{
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
          max-width: 1000px;
          margin: 0 auto;
        }}

        .video-card {{
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          overflow: hidden;
          transition: transform 0.2s;
        }}

        .video-card:hover {{
          transform: scale(1.03);
        }}

        video {{
          width: 100%;
          height: auto;
          display: block;
        }}

        .title {{
          padding: 10px;
          font-size: 16px;
          text-align: center;
          color: #222;
        }}

        a {{
          text-decoration: none;
          color: inherit;
        }}

        .user-info {{
          text-align: center;
          margin-bottom: 20px;
          padding: 10px;
          background: white;
          border-radius: 8px;
          max-width: 1000px;
          margin: 0 auto 20px;
        }}
      </style>
    </head>
    <body>
      <h1>KouTube!</h1>
      <div class="user-info">
        <p>ユーザーID: {user_id} でログイン中</p>
        <a href="upload.cgi">動画をアップロード</a> | <a href="logout.cgi">ログアウト</a>
      </div>
      <div class="video-grid">
    """)

    # 動画ごとの表示ブロック
    for v in videos:
        print(f"""
        <div class="video-card">
          <a href="video_view.cgi?video_id={v['id']}&user_id={user_id}">
            <video muted>
              <source src="{v['file_path']}" type="video/mp4">
            </video>
            <div class="title">{html.escape(v['title'])}</div>
          </a>
        </div>
        """)

    print("""
      </div>
    </body>
    </html>
    """)

    cursor.close()
    conn.close()

except Exception as e:
    print_error(f"予期しないエラー: {str(e)}\n{traceback.format_exc()}")
