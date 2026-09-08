import mysql.connector
from mysql.connector import Error
from datetime import datetime

class Memory:
    # connecting to database proj_iris
    def __init__(
        self,
        user_id="mandeep",  # logical identifier for conversation records (not database name)
        host="127.0.0.1",
        user="root",
        password="root",
        database="iris_db"
    ):
        self.user_id = user_id
        self.conn = self.connect(host, user, password, database)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.ensure_identity()

    # CONNECTION
    def connect(self, host, user, password, database):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                print("\nMySQL Connected!!!")
                return connection
            else:
                print("\nFailed to connect to MySQL server.")
        except Exception as e:
            print(f"Database connection failed! {e}")

    # TABLE CREATION
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                role VARCHAR(20),
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_summary (
                user_id VARCHAR(50) PRIMARY KEY,
                summary TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP 
                ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS identity (
                key_name VARCHAR(50) PRIMARY KEY,
                value TEXT
            )
        """)

        self.conn.commit()

    # PERMANENT IDENTITY
    def ensure_identity(self):
        default_values = {
            "creator_name": "Mandeep Singh",
            'creator_aliases': 'Mandeep,Mannu',
            "greeting_name" :"Mandeep",
            "assistant_name": "Iris",
            "core_identity": "Aurora"
        }

        for key, value in default_values.items():
            self.cursor.execute(
                "INSERT IGNORE INTO identity (key_name, value) VALUES (%s, %s)",
                (key, value)
            )

        self.conn.commit()

    def get_identity(self):
        self.cursor.execute("SELECT key_name, value FROM identity")
        rows = self.cursor.fetchall()
        return {key: value for key, value in rows}
    
    # CONVERSATION STORAGE
    def add(self, role, message):
        self.cursor.execute("""
            INSERT INTO conversations (user_id, role, message)
            VALUES (%s, %s, %s)
        """, (self.user_id, role, message))
        self.conn.commit()

    def get_recent(self, limit=10):
        self.cursor.execute("""
            SELECT role, message 
            FROM conversations
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
        """, (self.user_id, limit))

        rows = self.cursor.fetchall()
        rows.reverse()

        return [{"role": role, "content": msg} for role, msg in rows]

    def get_message_count(self):
        self.cursor.execute("""
            SELECT COUNT(*) FROM conversations
            WHERE user_id = %s
        """, (self.user_id,))
        return self.cursor.fetchone()[0]

    # SUMMARY MANAGEMENT
    def get_summary(self):
        self.cursor.execute("""
            SELECT summary FROM conversation_summary
            WHERE user_id = %s
        """, (self.user_id,))

        result = self.cursor.fetchone()
        return result[0] if result else ""

    def update_summary(self, new_summary):
        self.cursor.execute("""
            INSERT INTO conversation_summary (user_id, summary)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE summary = %s
        """, (self.user_id, new_summary, new_summary))

        self.conn.commit()

    # TRIMMING OLD CONVERSATIONS
    def trim_conversations(self, keep_last=10):
        self.cursor.execute(f"""
            DELETE FROM conversations
            WHERE user_id = %s
            AND id NOT IN (
                SELECT id FROM (
                    SELECT id FROM conversations
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                ) AS temp
            )
        """, (self.user_id, self.user_id, keep_last))

        self.conn.commit()

    # DATABASE HEALTH CHECK
    def is_database_connected(self):
        try:
            return self.conn.is_connected()
        except Exception:
            return False

    # CLEANUP
    def close(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("MySQL Connection Closed")

