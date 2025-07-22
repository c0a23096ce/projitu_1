#usr/bin/python3
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

    # データベース接続
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # すべての動画を取得（新しい順）
    cursor.execute("SELECT id, title, file_path FROM videos ORDER BY upload_at DESC")
    videos = cursor.fetchall()

    print("""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <title>KouTube - トップページ</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 0;
          background-color: #f5f5f5;
        }
        header {
          background-color: #ff4d4d;
          color: white;
          padding: 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .logo {
          display: flex;
          align-items: center;
          font-weight: bold;
          font-size: 1.5em;
          text-decoration: none;
          color: white;
        }
        .logo-icon {
          background: white;
          color: #ff4d4d;
          padding: 5px 10px;
          border-radius: 5px;
          margin-right: 10px;
        }
        .search-container {
          flex-grow: 1;
          margin: 0 20px;
          display: flex;
          align-items: center;
        }
        .search-form {
          flex-grow: 1;
          display: flex;
        }
        .search-input {
          flex-grow: 1;
          padding: 8px;
          font-size: 1em;
        }
        .search-btn, .voice-search {
          padding: 8px 12px;
          font-size: 1em;
          cursor: pointer;
        }
        .header-right {
          display: flex;
          gap: 10px;
        }
        .upload-btn, .profile-btn, .menu-btn, .icon-btn {
          background: white;
          border: none;
          padding: 8px 12px;
          font-size: 1em;
          cursor: pointer;
          border-radius: 5px;
        }

        .video-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
          padding: 40px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .video-card {
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          overflow: hidden;
          transition: transform 0.2s;
        }

            .video-card:hover {{
              transform: scale(1.03);
            }}

        .video-card video {
          width: 100%;
          display: block;
        }

        .video-title {
          padding: 10px;
          text-align: center;
          font-size: 18px;
          font-weight: bold;
          color: #333;
        }

        footer {
          background-color: #222;
          color: #ccc;
          text-align: center;
          padding: 15px;
          margin-top: 40px;
        }

        .sidebar {
          width: 250px;
          background: #fff;
          position: fixed;
          top: 0;
          bottom: 0;
          left: -250px;
          overflow-y: auto;
          transition: left 0.3s;
          box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }

        .sidebar.open {
          left: 0;
        }

        .sidebar-section {
          padding: 20px;
        }

        .sidebar-title {
          font-size: 1.2em;
          margin-bottom: 10px;
        }

        .sidebar-item {
          display: flex;
          align-items: center;
          padding: 10px 0;
          text-decoration: none;
          color: #333;
        }

        .sidebar-item-icon {
          margin-right: 10px;
        }

        .upload-modal {
          display: none;
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background: white;
          z-index: 9999;
          width: 400px;
          box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }

        .modal-content {
          padding: 20px;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .btn-primary, .btn-secondary {
          padding: 10px;
          border: none;
          cursor: pointer;
        }

        .btn-primary {
          background-color: #ff4d4d;
          color: white;
        }

        .btn-secondary {
          background-color: #ccc;
        }

        .upload-area {
          padding: 40px;
          text-align: center;
          border: 2px dashed #ccc;
          margin: 20px 0;
          cursor: pointer;
        }

        .upload-icon {
          font-size: 2em;
        }

        .upload-actions {
          display: flex;
          justify-content: space-between;
        }
      </style>
    </head>
    <body>

    <header>
      <button class="menu-btn" onclick="toggleSidebar()">☰</button>
      <a href="#" class="logo">
        <div class="logo-icon">VT</div>
        <div class="logo-text">VidTube Pro</div>
      </a>
      <div class="search-container">
        <form class="search-form">
          <input type="text" class="search-input" placeholder="動画、チャンネル、クリエイターを検索...">
          <button type="submit" class="search-btn">🔍</button>
        </form>
        <button class="voice-search">🎤</button>
      </div>
      <div class="header-right">
        <button class="upload-btn" onclick="openUploadModal()">📹 作成</button>
        <button class="icon-btn" onclick="openAuthModal()">👤</button>
        <button class="profile-btn">U</button>
      </div>
    </header>

    <nav class="sidebar" id="sidebar">
      <div class="sidebar-section">
        <a href="#" class="sidebar-item active"><div class="sidebar-item-icon">🏠</div>ホーム</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">🔥</div>急上昇</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">🎵</div>音楽</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">🎮</div>ゲーム</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">📺</div>映画</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">⚽</div>スポーツ</a>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-title">あなたへのおすすめ</div>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">📚</div>学習</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">🍳</div>料理</a>
        <a href="#" class="sidebar-item"><div class="sidebar-item-icon">🎨</div>アート</a>
      </div>
      
      <div class="search-form">
        <h2>動画検索</h2>
        <form method="get" action="video_search.cgi">
            <input type="text" name="title" placeholder="動画タイトルを入力">
            <input type="submit" value="検索">
        </form>
      </div>
      
    </nav>

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

    <!-- 認証モーダル -->
    <div class="upload-modal" id="authModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 id="authTitle">Sign In</h2>
          <button class="close-btn" onclick="closeAuthModal()">×</button>
        </div>
        <div id="signInForm">
          <input type="text" placeholder="Username" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="password" placeholder="Password" style="width:100%;padding:10px;margin-bottom:10px;" />
          <button class="btn-primary" style="width:100%;">Sign In</button>
          <p style="text-align:center;">
            Don't have an account? <a href="#" style="color:#4facfe;" onclick="toggleAuthForm()">Sign Up</a>
          </p>
        </div>
        <div id="signUpForm" style="display:none;">
          <input type="text" placeholder="First Name" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="text" placeholder="Last Name" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="email" placeholder="Email" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="text" placeholder="Username" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="password" placeholder="Password" style="width:100%;padding:10px;margin-bottom:10px;" />
          <input type="password" placeholder="Confirm Password" style="width:100%;padding:10px;margin-bottom:10px;" />
          <button class="btn-primary" style="width:100%;">Sign Up</button>
          <p style="text-align:center;">
            Already have an account? <a href="#" style="color:#4facfe;" onclick="toggleAuthForm()">Sign In</a>
          </p>
        </div>
      </div>
    </div>

    <!-- アップロードモーダル -->
    <div class="upload-modal" style="display:none;">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title">動画をアップロード</div>
          <button class="close-btn" onclick="closeUploadModal()">×</button>
        </div>
        <div class="upload-area" id="upload-area">
          <div class="upload-icon">⬆️</div>
          <div class="upload-text">ここにファイルをドロップ</div>
          <div class="upload-subtitle">またはクリックして選択</div>
          <input type="file" style="display:none;" id="fileInput">
        </div>
        <div class="upload-actions">
          <button class="btn-secondary" onclick="closeUploadModal()">キャンセル</button>
          <button class="btn-primary">アップロード</button>
        </div>
      </div>
    </div>

    <footer>
      &copy; 2025 KouTube Inc. All rights reserved.
    </footer>

    <script>
      function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('open');
      }
      function openUploadModal() {
        document.querySelectorAll('.upload-modal')[1].style.display = 'block';
      }
      function closeUploadModal() {
        document.querySelectorAll('.upload-modal')[1].style.display = 'none';
      }
      function openAuthModal() {
        document.getElementById('authModal').style.display = 'block';
      }
      function closeAuthModal() {
        document.getElementById('authModal').style.display = 'none';
      }
      function toggleAuthForm() {
        const signIn = document.getElementById('signInForm');
        const signUp = document.getElementById('signUpForm');
        const title = document.getElementById('authTitle');
        if (signIn.style.display === 'none') {
          signIn.style.display = 'block';
          signUp.style.display = 'none';
          title.textContent = 'Sign In';
        } else {
          signIn.style.display = 'none';
          signUp.style.display = 'block';
          title.textContent = 'Sign Up';
        }
      }

      const uploadArea = document.getElementById('upload-area');
      if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
          e.preventDefault();
          uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', () => {
          uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', (e) => {
          e.preventDefault();
          uploadArea.classList.remove('dragover');
          const files = e.dataTransfer.files;
          alert(`${files.length} ファイルがドロップされました。`);
        });
        uploadArea.addEventListener('click', () => {
          document.getElementById('fileInput').click();
        });
      }
    </script>

    </body>
    </html>
    """)

except Exception as e:
    print_error(f"予期しないエラー: {str(e)}\n{traceback.format_exc()}")

finally:
  conn.close()
