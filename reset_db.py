import mysql.connector
import crypt

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='passwordA1!',
    charset='utf8'
)
cursor = conn.cursor()
cursor.execute("DROP DATABASE IF EXISTS KouTube")
cursor.execute("CREATE DATABASE KouTube")
cursor.execute("USE KouTube")

tables = [
    """CREATE TABLE users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(50) NOT NULL UNIQUE,
      password VARCHAR(255) NOT NULL,
      email VARCHAR(100) NOT NULL UNIQUE,
      fname VARCHAR(50),
      lname VARCHAR(50)
    )""",
    
    """CREATE TABLE videos (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      title VARCHAR(100) NOT NULL,
      description TEXT,
      file_path VARCHAR(255) NOT NULL,
      view_count INT DEFAULT 0,
      upload_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )""",
    
    """CREATE TABLE comments (
      id INT AUTO_INCREMENT PRIMARY KEY,
      video_id INT NOT NULL,
      user_id INT NOT NULL,
      content TEXT NOT NULL,
      wrote_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (video_id) REFERENCES videos(id),
      FOREIGN KEY (user_id) REFERENCES users(id)
    )""",
    
    """CREATE TABLE likes (
      id INT AUTO_INCREMENT PRIMARY KEY,
      video_id INT NOT NULL,
      user_id INT NOT NULL,
      liked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      UNIQUE (video_id, user_id),
      FOREIGN KEY (video_id) REFERENCES videos(id),
      FOREIGN KEY (user_id) REFERENCES users(id)
    )""",
    
    """CREATE TABLE sessions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL UNIQUE,
      session_id VARCHAR(255) NOT NULL UNIQUE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      expires_at DATETIME,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )""",
    
    """CREATE TABLE dislikes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        video_id INT NOT NULL,
        user_id INT NOT NULL,
        disliked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_dislike (video_id, user_id),
        FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )"""
]

for table_query in tables:
    cursor.execute(table_query)

insert_user = [
    {"username": "Taku18",
     "password": "passwordA1!",
     "email": "taku18@example.com",
     "fname" : "工科",
     "lname" : "太郎"
    },
    {"username": "sera",
     "password": "passwordA1!",
     "email": "sera@example.com",
     "fname" : "工科",
     "lname" : "太郎"
    },
    {"username": "kaede_2025j",
     "password": "passwordA1!",
     "email": "kaede_2025j@example.com",
     "fname" : "工科",
     "lname" : "太郎"
    },
    {"username": "eisho",
     "password": "passwordA1!",
     "email": "eisho@example.com",
     "fname" : "工科",
     "lname" : "太郎"
    }
]

for user in insert_user:
    salt = crypt.mksalt(crypt.METHOD_SHA512)
    hashed_password = crypt.crypt(user["password"], salt)
    query = f"""
    INSERT INTO users (username, password, email, fname, lname) VALUES
    (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user["username"], hashed_password, user["email"], user["fname"], user["lname"]))

insert_video = """
INSERT INTO videos (user_id, title, description, file_path, view_count, upload_at) VALUES
(1, 'ギター練習記#1', 'ギター練習', '/project/projitu_1/videos/71823308bf2b400f97bcd9e81f4ac369.mp4', 0, '2025-07-24 21:55:52'),
(2, 'ヤモリの食事', 'ヤモリの裏', '/project/projitu_1/videos/364eeffca79847178f19b71cd666bef4.mp4', 0, '2025-07-24 21:58:15'),
(3, 'ポケモンGO色違いシリーズ', 'ポケモンGOボックス画面', '/project/projitu_1/videos/2e4acb080b8f43a3b0d784329d28b89a.mp4', 0, '2025-07-24 21:59:44'),
(4, 'RideLink紹介動画', 'RideLink紹介動画', '/project/projitu_1/videos/b2edfa739620481cbe68fb756e4c13a7.mp4', 0, '2025-07-24 22:01:26');
"""

cursor.execute(insert_video)



conn.commit()
cursor.close()
conn.close()