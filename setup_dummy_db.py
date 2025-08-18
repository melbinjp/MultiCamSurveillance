import sqlite3
import time

db_connection = sqlite3.connect("video_analytics.db")
cursor = db_connection.cursor()

# Create a table to store batch information
cursor.execute('''CREATE TABLE IF NOT EXISTS batches
                (batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id TEXT,
                starting_frame_id INTEGER,
                ending_frame_id INTEGER,
                timestamp INTEGER)''')

# Create a table to store frame counts
cursor.execute('''CREATE TABLE IF NOT EXISTS camera_frame_count
                (camera_id TEXT PRIMARY KEY,
                frame_count INTEGER)''')

# Insert a dummy batch record
# The timestamp 1723896000 corresponds to the start of the batch
# The frames are from 1 to 5.
cursor.execute("INSERT INTO batches (camera_id, starting_frame_id, ending_frame_id, timestamp) VALUES (?, ?, ?, ?)",
               ('Camera_0', 1, 5, 1723896000))

# Insert a dummy frame count
cursor.execute("INSERT OR REPLACE INTO camera_frame_count (camera_id, frame_count) VALUES (?, ?)",
               ('Camera_0', 5))

db_connection.commit()
db_connection.close()

print("Database initialized with dummy data.")
