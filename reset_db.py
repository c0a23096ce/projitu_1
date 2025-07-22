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

salt = crypt.mksalt(crypt.METHOD_SHA512)
hashed_password = crypt.crypt("password1", salt)


insert_user = f"""
INSERT INTO users (username, password, email, fname, lname) VALUES
('user1', '{hashed_password}', 'user1@example.com', 'User', 'One')
"""

cursor.execute(insert_user)

insert_video = """
INSERT INTO videos (user_id, title, description, file_path, view_count, upload_at) VALUES
(1, 'テスト動画', 'これはテスト用の説明です', '/project/projitu_1/project/projitu_1/videos/test.mp4', 0, '2025-07-11 17:00:00'),
(1, '飛行機の映像', '飛行機が飛んでるよ', '/project/projitu_1/videos/hikouki.mp4', 0, '2025-07-11 17:42:36'),
(1, '海', '自然の風景', '/project/projitu_1/videos/umi.mp4', 0, '2025-07-11 17:43:32'),
(1, '教会の荘厳な佇まい', '静けさと歴史を感じる古い教会の映像です。', '/project/projitu_1/videos/church.mp4', 0, '2025-07-18 14:10:36'),
(1, '滝の迫力映像', '豪快に流れる滝と自然の音を収録。', '/project/projitu_1/videos/taki.mp4', 0, '2025-07-18 14:10:36'),
(1, '自然の中のひととき', '森の中での癒やしのひとときをお届けします。', '/project/projitu_1/videos/nature.mp4', 0, '2025-07-18 14:10:36');
"""

cursor.execute(insert_video)

conn.commit()
cursor.close()
conn.close()