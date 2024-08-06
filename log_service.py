from flask import g
import json, time, uuid, sqlite3
from datetime import datetime
import math


class LogService():
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        # 初始化連接（只執行一次）
        self.conn = sqlite3.connect('./sqlite/log_storage.db')
        self.cursor = self._instance.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                log_entry TEXT,
                timestamp INTEGER
            )
        ''')

    def store_message(self, raw: str):
        try:
            body:dict = json.loads(raw)
            events:list = body.get("events")
            user_id = uuid.uuid4()
            timestamp = math.floor(time.time()*1000)
            if (events.__len__() > 0):
                for event in events:
                    event:dict
                    source:dict = event.get("source")
                    if ("type" in source and source.get("type") == "user"):
                        user_id = source.get("userId")
                        break
            self.cursor.execute("INSERT INTO logs (user_id, log_entry, timestamp) VALUES (?, ?, ?)", (user_id, raw, timestamp))
            self.conn.commit()
        except Exception as e:
            print(e)

    def close(self):
        self.cursor.close()
        self.conn.close()
        LogService._instance = None