import uuid
import random
import string
import sqlite3

random.seed(90) 

class DistributedObject:
    def __init__(self, global_oid=None):
        self.global_oid = global_oid if global_oid else str(uuid.uuid4())

class SyncRecord(DistributedObject):
    def __init__(self, record_id, metadata, trust_score=None, global_oid=None):
        super().__init__(global_oid)
        self.record_id = record_id
        self.metadata = metadata
        self.trust_score = trust_score if trust_score is not None else random.uniform(10.5, 99.9)
        self.history_logs = []                              

    def add_history(self, event_id, status):
        self.history_logs.append({"event_id": event_id, "status": status})

def generate_1000_objects():
    dataset = []
    for i in range(1000):
        random_meta = ''.join(random.choices(string.ascii_letters, k=15))
        obj = SyncRecord(record_id=i, metadata=random_meta)
        for _ in range(random.randint(1, 3)):
            obj.add_history(
                event_id=random.randint(1000, 9999),
                status=random.choice(["CREATED", "UPDATED", "SYNCED"])
            )
        dataset.append(obj)
    return dataset

def save_original_to_sqlite(dataset, db_path="site_a_local.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS original_records (
        global_oid TEXT PRIMARY KEY, record_id INTEGER, metadata TEXT, trust_score REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS original_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, global_oid TEXT, event_id INTEGER, status TEXT,
        FOREIGN KEY(global_oid) REFERENCES original_records(global_oid))''')
    
    cursor.execute("DELETE FROM original_records")
    cursor.execute("DELETE FROM original_logs")
    
    for obj in dataset:
        cursor.execute('INSERT INTO original_records VALUES (?, ?, ?, ?)',
                       (obj.global_oid, obj.record_id, obj.metadata, obj.trust_score))
        for log in obj.history_logs:
            cursor.execute('INSERT INTO original_logs (global_oid, event_id, status) VALUES (?, ?, ?)',
                           (obj.global_oid, log["event_id"], log["status"]))
            
    conn.commit()
    conn.close()

def fetch_from_sqlite(db_path="site_a_local.db"):
    """Đọc dữ liệu từ SQLite và tái tạo Object trên RAM"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM original_records')
    records = cursor.fetchall()
    
    dataset = []
    for row in records:
        global_oid, record_id, metadata, trust_score = row
        obj = SyncRecord(record_id, metadata, trust_score, global_oid)
        
        cursor.execute('SELECT event_id, status FROM original_logs WHERE global_oid=?', (global_oid,))
        for log_row in cursor.fetchall():
            obj.add_history(log_row[0], log_row[1])
            
        dataset.append(obj)
    conn.close()
    return dataset