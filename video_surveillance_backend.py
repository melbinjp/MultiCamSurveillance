import cv2
import numpy as np
import copy
import random
import threading
import json
import time
import os
import sqlite3
import logging
import configparser
import concurrent.futures

# Shared dictionary to hold camera feed threads
camera_threads = {}

available_camera_ids = []  # List to store available camera IDs

# Initialize the configuration parser
config = configparser.ConfigParser()
config.read('config.ini')

# Read configuration values
batch_duration = int(config['General']['batch_duration'])
log_file = config['General']['log_file']
log_level = config['General']['log_level']

# Create the "logs" folder if it doesn't exist
os.makedirs("logs", exist_ok=True)
# Configure logging
logging.basicConfig(filename=log_file, level=logging.getLevelName(log_level), format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the database connection pool
def init_db_pool():
    return sqlite3.connect("video_analytics.db", check_same_thread=False)

# Create a database connection pool
db_connection_pool = init_db_pool()

# Database setup
def setup_database():
    with db_connection_pool:
        cursor = db_connection_pool.cursor()

        # Create a table to store batch information
        cursor.execute('''CREATE TABLE IF NOT EXISTS batches
                        (batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        camera_id TEXT,  -- Add a column for camera ID or name
                        starting_frame_id INTEGER,
                        ending_frame_id INTEGER,
                        timestamp INTEGER)''')

        # Create a table to store frame counts
        cursor.execute('''CREATE TABLE IF NOT EXISTS camera_frame_count
                        (camera_id TEXT PRIMARY KEY,
                        frame_count INTEGER)''')



# Function to log batch information to the database
def log_batch_info(camera_id, starting_frame_id, ending_frame_id, timestamp):
   with db_connection_pool:
        cursor = db_connection_pool.cursor()
        cursor.execute("INSERT INTO batches (camera_id,starting_frame_id, ending_frame_id, timestamp) VALUES (?, ?, ?, ?)",
                       (camera_id, starting_frame_id, ending_frame_id, timestamp))

# Function to retrieve frame count for a camera from the database
def get_frame_count(camera_id):
    with db_connection_pool:
        cursor = db_connection_pool.cursor()
        cursor.execute("SELECT frame_count FROM camera_frame_count WHERE camera_id = ?", (camera_id,))
        row = cursor.fetchone()
        if row:
            print(row[0])
            return row[0]
        else:
            return 0


# Function to update frame count for a camera in the database
def update_frame_count(camera_id, frame_count):
    try:
        with db_connection_pool:
            cursor = db_connection_pool.cursor()
            cursor.execute("INSERT OR REPLACE INTO camera_frame_count (camera_id, frame_count) VALUES (?, ?)",
                        (camera_id, frame_count))
    except Exception as e:
        logging.error(f'Exception occures: {str(e)}')

def get_current_coordinates():
    #function to retrieve the longitude and latitude data
    pass

def create_camera_feeds(camera_index):
   
    # Initialize a VideoCapture object for the camera
    cap = cv2.VideoCapture(camera_index)  # Use camera with index 'i'
    
    # Check if the camera was opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}.")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Check if the fps value is valid (some cameras may not provide it)
    if fps > 0:
        print(f"Frames per Second (FPS): {fps}")
    else:
        print("FPS information not available for this camera feed. setting fps to 25")
        fps = 25

    try:
        latitude, longitude = get_current_coordinates()
    except Exception as e:
        # Generate some random geolocation information (latitude and longitude)
        latitude, longitude = (0, 0)#round(random.uniform(-90, 90), 6)

    # Create camera metadata
    metadata = {
        'camera_name': f'Camera_{camera_index}',
        'geolocation': f'({latitude}, {longitude})',
        'fps':fps,
        'cap': cap,  # Store the VideoCapture object
    }

    return metadata

def process_and_save_frames(metadata):
    camera_id = metadata['camera_name']
    frame_id = get_frame_count(camera_id)  # Retrieve frame count from the database

    fps = metadata['fps']

    # Create a directory for each camera if it doesn't exist
    camera_folder = os.path.join("images", camera_id)
    os.makedirs(camera_folder, exist_ok=True)

    # Variables for batch processing
    start_time = int(time.time())
    batch_start_frame = 0
    frame_count = 0 

    while True:
        # Capture a frame from the camera feed
        ret, frame = metadata['cap'].read()
        if not ret:
            break

        frame_id += 1
        
        try:
            # Process and create a JSON object for one frame per second
            if frame_id % fps == 0:
                timestamp = int(time.time())  # Unix timestamp
                frame_info = {
                    "camera_id": camera_id,
                    "frame_id": frame_id,
                    "geo_location": metadata["geolocation"],
                    "timestamp": timestamp,
                }

                # Write the frame as a jpg image file
                image_path = os.path.join(camera_folder, f"frame_{frame_id}.jpg")
                cv2.imwrite(image_path, frame)
                frame_info["image_path"] = image_path


                # Convert the frame information to JSON
                frame_json = json.dumps(frame_info)

                # Log JSON data with INFO level
                logging.info(frame_json)
                
                #print JSON 
                print(frame_json)

            # Check if the batch duration has been reached
            if int(time.time()) - start_time >= batch_duration:
                batch_start_frame = (frame_id - frame_count)
                log_batch_info(camera_id, batch_start_frame, frame_id, start_time)
                print(f'start frame id = {batch_start_frame}------ending frame id = {frame_id}-----timestamp{timestamp}-----start_time{start_time}')
                batch_start_frame = frame_id
                start_time = int(time.time())
                frame_count = 0
        except Exception as e:
            #Log exceptions with ERROR level
            logging.error(f'Exception occures: {str(e)}')

        update_frame_count(camera_id, frame_id)  # Update frame count in the database

def check_available_cameras(interval=5):
    global available_camera_ids
    while True:
        camera_ids = []
        camera_id = 0
        while True:
            cap = cv2.VideoCapture(camera_id)
            if not cap.isOpened():
                break
            camera_ids.append(camera_id)
            cap.release()
            camera_id += 1
        available_camera_ids = camera_ids
        time.sleep(interval)

# Create a thread to periodically check for available cameras
camera_check_thread = threading.Thread(target=check_available_cameras)
camera_check_thread.daemon = True  # Make the thread a daemon so it exits when the main program does
camera_check_thread.start()

# Create the "images" folder if it doesn't exist
os.makedirs("images", exist_ok=True)

#set up the database
setup_database()

# Initialize the copy of active_camera_ids
previous_active_camera_ids = copy.copy(available_camera_ids)

while True:
    active_camera_ids = available_camera_ids
    print(len(active_camera_ids))

    # Check if camera IDs have changed
    if set(active_camera_ids) != set(previous_active_camera_ids):
        # Update the copy of active_camera_ids
        previous_active_camera_ids = copy.copy(active_camera_ids)

        # Check for removed cameras and stop their threads
        for camera_id in list(camera_threads.keys()):
            if camera_id not in active_camera_ids:
                camera_threads[camera_id]['stop'] = True
                del camera_threads[camera_id]

        # Use a ThreadPoolExecutor to manage the threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(active_camera_ids) * 2) as executor:
            # Create camera feeds concurrently
            camera_feeds = []
            for camera_id in active_camera_ids:
                if camera_id not in camera_threads:
                    # New camera detected, start a new thread
                    camera_threads[camera_id] = {'stop': False}
                    metadata = executor.submit(create_camera_feeds, camera_id)
                    camera_feeds.append(metadata)
            # Process frames concurrently
            for camera_feed in camera_feeds:
                metadata = camera_feed.result()
                if metadata:
                    executor.submit(process_and_save_frames, metadata)
    