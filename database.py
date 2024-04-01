import mysql.connector

# MySQL 연결 설정
def connect_to_database():
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="doslTkfkd12!",
        database="OSSP"
    )
    return db_connection


def get_users():
    db_connection = connect_to_database()
    db_cursor = db_connection.cursor()
    
    query = "S F W"
    db_cursor.execute(query)
    
    # 조회된 정보 가져오기
    users = db_cursor.fetchall()
    
    db_cursor.close()
    db_connection.close()
    
    return users
    