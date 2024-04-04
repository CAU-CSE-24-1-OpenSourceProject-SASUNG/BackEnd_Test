import mysql.connector
from mysql.connector import Error
from typing import Optional

class Database:
    def __init__(self, host_name: str, user_name: str, user_password: str, db_name: str):
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """ 데이터베이스에 연결을 시도합니다. """
        if self.connection is None:
            try:
                self.connection = mysql.connector.connect(
                    host=self.host_name,
                    user=self.user_name,
                    passwd=self.user_password,
                    database=self.db_name
                )
                #print("MySQL Database connection successful")
            except Error as e:
                print(f"The error '{e}' occurred")

    def execute_query(self, query: str):
        """ 데이터베이스에 쿼리를 실행합니다. """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query successful")
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, query: str):
        """ 데이터베이스에서 읽기 쿼리를 실행합니다. """
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")