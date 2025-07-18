#!/usr/bin/env python3
import cgi, os, mysql.connector, http.cookies, time, html
from utils import require_login, get_connection

UPLOAD_DIR = "/var/www/html/project/projitu_1/videos"

print("Content-Type: text/html; charset=utf-8\n")

html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>動画アップロード</title>
</head>
<body>
    <h2>動画アップロード</h2>
    {message}
    <form action="upload.cgi" method="post" enctype="multipart/form-data">
        タイトル: <input type="text" name="title"><br>
        説明: <textarea name="description"></textarea><br>
        動画ファイル: <input type="file" name="video"><br>
        <input type="submit" value="アップロード">
    </form>
    {extra}
</body>
</html>
'''

# セッション確認
user_id = require_login()

form = cgi.FieldStorage()
message = ""
extra = ""

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
            video_path = os.path.join(UPLOAD_DIR, video_file)
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
video_list_html = ""
try:
    db = get_connection()
    cursor = db.cursor()
    query = f"SELECT id, title, file_path FROM videos WHERE user_id='{user_id}'"
    cursor.execute(query)
    for vid, title, file_path in cursor.fetchall():
        video_list_html += f"""
        <div>
            <video controls src="/project/projitu_1/videos/{file_path}" width="240"></video><br>
            タイトル: {title}
            <form method="post" action="upload.cgi" style="display:inline;">
                <input type="hidden" name="delete" value="{vid}">
                <input type="submit" value="削除">
            </form>
        </div>
        <hr>
        """
    db.close()
except Exception as e:
    video_list_html = f"<p style='color:red'>一覧取得エラー: {str(e)}</p>"

# HTML表示
fileitem = form["video"] if "video" in form else None
if fileitem is None or not getattr(fileitem, "filename", None):
    print(html_template.format(message=message, extra=video_list_html))
else:
    title = form.getvalue("title", "")
    description = form.getvalue("description", "")

    if not fileitem.filename:
        message = "<p style='color:red'>動画ファイルが未選択です</p>"
        print(html_template.format(message=message, extra=""))
    else:
        filename = os.path.basename(fileitem.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(fileitem.file.read())

            db = get_connection()
            
            cursor = db.cursor()
            # SQLインジェクション脆弱性あり（意図的）
            query = f"INSERT INTO videos (user_id, title, description, file_path) VALUES ('{user_id}', '{title}', '{description}', '{filename}')"
            cursor.execute(query)
            db.commit()
            db.close()

            message = f"<p>アップロード成功: {title}</p>"
            extra = f"""<video controls src="/project/projitu_1/videos/{filename}" width="480"></video><br>
                        <a href="upload.cgi">戻る</a>"""
            print(html_template.format(message=message, extra=video_list_html + extra))
        except Exception as e:
            message = f"<p style='color:red'>エラー: {str(e)}</p>"
            print(html_template.format(message=message, extra=""))
