import mysql.connector

# DB 연결 정보 (사용자 정보에 맞게 수정하세요!)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "bangu"
DB_PORT = 3310

 
class DataManager:
    """데이터베이스와 상호작용하는 모델 클래스"""
    
    def get_db_connection(self):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            return conn
        except mysql.connector.Error as err:
            print(f"DB 연결 오류: {err}")
            return None

    def get_all_items(self):
        """데이터베이스에서 모든 항목을 가져오는 함수"""
        conn = self.get_db_connection()
        if not conn:
            return [], [], []
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM room")
            items = cursor.fetchall()
            cursor.execute("SELECT * FROM images")
            imgs = cursor.fetchall()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            return items, imgs, users
        except mysql.connector.Error as err:
            print(f"쿼리 실행 오류: {err}")
            return [], [], []
        finally:
            cursor.close()
            conn.close()

    def get_user_by_username(self, username):
        """
        사용자 아이디로 사용자 정보를 가져오는 함수
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            print(f"쿼리 실행 오류: {err}")
            return None
        finally:
            cursor.close()
            conn.close()

    def add_user(self, username, password, nickname, birth, gender):
        """
        새로운 사용자를 데이터베이스에 추가하는 함수
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            sql = "INSERT INTO users (username, password, nickname, birth, gender) VALUES (%s, %s, %s, %s, %s)"
            val = (username, password, nickname, birth, gender)
            cursor.execute(sql, val)
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"쿼리 실행 오류: {err}")
            return False
        finally:
            cursor.close()
            conn.close()
