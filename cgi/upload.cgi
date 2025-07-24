#!/usr/bin/env python3
import cgi, os, mysql.connector, http.cookies, time, html
from utils import require_login, get_connection
import uuid

UPLOAD_DIR = "/var/www/html/project/projitu_1/videos"
PUBLOIC_DIR = "/project/projitu_1/videos"

print("Content-Type: text/html; charset=utf-8\n")

html_template = '''
<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>動画アップロード</title>
        <link rel="stylesheet" href="../static/background.css">
        <link rel="stylesheet" href="../static/header.css">
        <link rel="stylesheet" href="../static/upload.css">
        <script src="../static/header.js" defer></script>
        <script src="../static/upload.js" defer></script>
    </head>
    <body>
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
                        <input type="text" name="title" value="{current_title}" class="search-input" placeholder="動画、チャンネル、クリエイターを検索...">
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
            <div class="upload-container">
                <div class="upload-title">動画アップロード</div>
                {message}
                <form class="upload-form" action="upload.cgi" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label class="form-label" for="title">タイトル</label>
                        <input type="text" id="title" name="title" class="form-input" placeholder="動画タイトルを入力">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="description">説明</label>
                        <textarea id="description" name="description" class="form-input form-textarea" placeholder="動画の説明"></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">動画ファイル</label>
                        <div class="file-upload-area">
                            <span class="file-upload-icon">📹</span>
                            <div class="file-upload-text">ここにファイルをドラッグ＆ドロップ</div>
                            <div class="file-upload-hint">対応形式: mp4, mov, avi, webm</div>
                            <input type="file" name="video" class="file-input">
                        </div>
                    </div>
                    <button type="submit" class="upload-btn-submit">アップロード</button>
                </form>
                <div class="video-list-container">
                    <div class="video-list-title">あなたの動画一覧</div>
                    {extra}
                </div>
            </div>
        </div>
    </body>
</html>
'''

# セッション確認
user_id = require_login()

form = cgi.FieldStorage()
message = ""
extra = ""
current_title = form.getfirst('title', '')

# 動画削除処理
if form.getvalue("delete"):
    delete_id = form.getvalue("delete")
    try:
        db = get_connection()
        cursor = db.cursor()
        query = f"SELECT file_path FROM videos WHERE id='{delete_id}' AND user_id='{user_id}'"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            video_file = row[0]
            video_path = os.path.join("/var/www/html", video_file.lstrip("/"))
            if os.path.exists(video_path):
                os.remove(video_path)
            query = f"DELETE FROM videos WHERE id='{delete_id}' AND user_id='{user_id}'"
            cursor.execute(query)
            db.commit()
        db.close()
        message = "<p>動画を削除しました</p>"
    except Exception as e:
        message = f"<p style='color:red'>削除エラー: {str(e)}</p>"

# 動画一覧取得
video_list_html = '<div class="video-grid">'
try:
    db = get_connection()
    cursor = db.cursor()
    query = f"SELECT id, title, file_path FROM videos WHERE user_id='{user_id}'"
    cursor.execute(query)
    for vid, title, file_path in cursor.fetchall():
        video_list_html += f"""
        <div class="video-item">
            <video class="video-preview" controls src="{file_path}" poster="" ></video>
            <div class="video-title">{html.escape(title)}</div>
            <div class="video-actions">
                <form method="post" action="upload.cgi" style="display:inline;">
                    <input type="hidden" name="delete" value="{vid}">
                    <button type="submit" class="delete-btn">削除</button>
                </form>
            </div>
        </div>
        """
    video_list_html += '</div>'
    db.close()
except Exception as e:
    video_list_html = f"<p style='color:red'>一覧取得エラー: {str(e)}</p>"

# HTML表示
fileitem = form["video"] if "video" in form else None
if fileitem is None or not getattr(fileitem, "filename", None):
    print(html_template.format(message=message, extra=video_list_html, current_title=current_title))
else:
    title = form.getvalue("title", "")
    description = form.getvalue("description", "")

    if not fileitem.filename:
        message = "<p style='color:red'>動画ファイルが未選択です</p>"
        print(html_template.format(message=message, extra="", current_title=current_title))
    else:
        # ランダムなファイル名を生成
        ext = os.path.splitext(fileitem.filename)[1].lower()
        # 許可する拡張子
        allowed_exts = ['.mp4', '.mov', '.avi', '.webm']
        if ext not in allowed_exts:
            message = "<p style='color:red'>許可されていないファイル形式です</p>"
            print(html_template.format(message=message, extra="", current_title=current_title))
        else:
            safe_filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, safe_filename)
            try:
                with open(filepath, 'wb') as f:
                    f.write(fileitem.file.read())
                    
                public_filepath = os.path.join(PUBLOIC_DIR, safe_filename)
                db = get_connection()
                cursor = db.cursor()
                query = f"INSERT INTO videos (user_id, title, description, file_path) VALUES ('{user_id}', '{title}', '{description}', '{public_filepath}')"
                cursor.execute(query)
                db.commit()
                db.close()

                message = f"<p>アップロード成功: {title}</p>"
                extra = f"""<video controls src="/project/projitu_1/videos/{safe_filename}" width="480"></video><br>
                            <a href="upload.cgi">戻る</a>"""
                print(html_template.format(message=message, extra=video_list_html + extra, current_title=current_title))
            except Exception as e:
                message = f"<p style='color:red'>エラー: {str(e)}</p>"
                print(html_template.format(message=message, extra="", current_title=current_title))
