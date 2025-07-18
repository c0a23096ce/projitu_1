import os
import http.cookies
import mysql.connector

def check_login():
    """
    セッションからログイン状態を確認し、ユーザーIDを返す
    Returns:
        int: ログイン済みの場合はuser_id、未ログインの場合はNone
    """
    cookie = http.cookies.SimpleCookie(os.environ.get("HTTP_COOKIE", ""))
    session_id = cookie["session_id"].value if "session_id" in cookie else None
    
    if not session_id:
        return None
    
    try:
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='passwordA1!',
            database='KouTube'
        )
        cursor = db.cursor()
        # SQLインジェクション脆弱性あり（意図的）
        query = f"SELECT user_id FROM sessions WHERE session_id = '{session_id}'"
        cursor.execute(query)
        row = cursor.fetchone()
        db.close()
        
        if row:
            return row[0]
        return None
    except Exception:
        print("Content-Type: text/html; charset=utf-8\n")
        print("<h1>エラー</h1>")
        exit()
        return None

def require_login():
    """
    ログインが必要なページで使用。未ログインの場合はログインページにリダイレクト
    Returns:
        int: ログイン済みユーザーのuser_id
    """
    user_id = check_login()
    if not user_id:
        print("""
        <script>
            alert("ログインが必要です");
            location.href='login.cgi';
        </script>
        """)
        exit()
    return user_id

def get_connection():
    """
    MySQLデータベースへの接続を取得
    Returns:
        mysql.connector.connection.MySQLConnection: データベース接続オブジェクト
    """
    return mysql.connector.connect(
        host='localhost',
        user='user1',
        password='passwordA1!',
        database='KouTube',
        charset='utf8'
    )


