import mysql.connector

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        self.conn = mysql.connector.connect(**self.config)

    def execute(self, sql, params=None):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params or ())
            self.conn.commit()
            return cur.lastrowid
        except mysql.connector.errors.OperationalError:
            self.connect()  # herverbinden en opnieuw proberen
            cur = self.conn.cursor()
            cur.execute(sql, params or ())
            self.conn.commit()
            return cur.lastrowid

    def fetchone(self, sql, params=None):
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute(sql, params or ())
            return cur.fetchone()
        except mysql.connector.errors.OperationalError:
            self.connect()  # herverbinden en opnieuw proberen
            cur = self.conn.cursor()
            cur.execute(sql, params or ())
            return cur.fetchone()

    def fetchall(self, sql, params=None):
        try:
            cur = self.conn.cursor(dictionary=True)    
            cur.execute(sql, params or ())
            return cur.fetchall()
        except mysql.connector.errors.OperationalError:
            self.connect()  # herverbinden en opnieuw proberen
            cur = self.conn.cursor()
            cur.execute(sql, params or ())
            return cur.fetchone()