import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='user1',
        password='passwordA1!',
        database='KouTube',
        charset='utf8'
    )
