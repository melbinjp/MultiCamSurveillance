import os
import json
import cv2
import sqlite3
import configparser
from datetime import datetime, timedelta
import logging

# Initialize the configuration parser
config = configparser.ConfigParser()
config.read('config.ini')

# Read configuration values
log_file = config['General']['log_file']
error_log_file = config['General']['error_log']
log_level = config['General']['log_level']
fps = int(config['General']['output_fps'])

# Configure logging
logging.basicConfig(filename = error_log_file, level=logging.getLevelName(log_level), format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the database connection pool
def init_db_pool():
    return sqlite3.connect("video_analytics.db", check_same_thread=False)

# Create a database connection pool
db_connection_pool = init_db_pool()
db_connection_pool.row_factory = sqlite3.Row  # Set row factory to use dictionaries

def get_available_timestamps_with_cameras():
    try:
        # Retrieve distinct timestamps from the database
        with db_connection_pool:
            cursor = db_connection_pool.cursor()
            cursor.execute("""
                SELECT DISTINCT timestamp, camera_id
                FROM batches
            """)

            timestamps_with_cameras = [(datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M:%S"), row[1]) for row in cursor.fetchall()]
            return timestamps_with_cameras
    except Exception as e:
        error_message = f"Error getting available timestamps with cameras: {str(e)}"
        logging.error(error_message, exc_info=True)
        return []

def find_nearest_batch(timestamp_with_cams, batch_duration):
    try:
        # Convert the timestamp to Unix timestamp
        unix_timestamp = int(datetime.strptime(timestamp_with_cams[0], "%Y-%m-%d %H:%M:%S").timestamp())
        camera_id = timestamp_with_cams[1]
        # Calculate the start and end timestamps for searching batches
        start_timestamp = unix_timestamp - batch_duration
        end_timestamp = unix_timestamp + batch_duration

        # Search for batches within the specified time range
        with db_connection_pool:
            cursor = db_connection_pool.cursor()
            cursor.execute("""
                SELECT *
                FROM batches
                WHERE timestamp BETWEEN ? AND ? AND camera_id = ?
                ORDER BY ABS(timestamp - ?)  -- Order by the absolute time difference
                LIMIT 1
            """, (start_timestamp, end_timestamp, camera_id, unix_timestamp))

        # Fetch the matching batch data
        batches = cursor.fetchone()

        if not batches:
            # If no exact match is found, find the closest batch
            with db_connection_pool:
                cursor = db_connection_pool.cursor()
                cursor.execute("""
                    SELECT *
                    FROM batches
                    WHERE camera_id = ?
                    ORDER BY ABS(timestamp - ?)  -- Order by the absolute time difference
                    LIMIT 1
                """, (camera_id, unix_timestamp))

            closest_batch = cursor.fetchone()
            print("no timestamp found within 60 seconds of the given timestamp the closest timestamp is"+str(closest_batch["timestamp"]))

            return closest_batch

        return batches
    except Exception as e:
        error_message = f"Error finding nearest batch: {str(e)}"
        logging.error(error_message, exc_info = True)
        return None

def extract_frames(batch, output_folder, duration):
    try:
        frames = []

        # Parse JSON log file and extract frames
        with open(log_file, 'r') as log:
            for line in log:
                try:
                    # Split the line at the first occurrence of "{"
                    parts = line.split("{", 1)
                    if len(parts) > 1:
                        # Extract the JSON portion (everything after the first "{")
                        json_data = "{" + parts[1]
                        frame_info = json.loads(json_data)
                        if (batch["timestamp"] <= frame_info["timestamp"]) and (batch["camera_id"]==frame_info["camera_id"]) and (batch["starting_frame_id"] <= frame_info["frame_id"]) and (frame_info["timestamp"] <= (batch["timestamp"] + duration)):
                            frames.append(frame_info)
                except json.JSONDecodeError:
                    # Handle lines that are not valid JSON (extra data)
                    continue
        if frames:
            print(f'{len(frames)} frames has been retrieved')
           
            sample_frame = cv2.imread(frames[0]["image_path"])
            # Check if the image was loaded successfully
            if sample_frame is not None:
                # Get the height and width of the image
                frame_height, frame_width, _ = sample_frame.shape
                print(f"Image Width: {frame_width} pixels")
                print(f"Image Height: {frame_height} pixels")
            else:
                frame_height, frame_width, _ = [640,480]
                print(f"Failed to load the image.using default resolution{frame_height}X{frame_width}")
                

            # Create a video from the selected frames
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(f'{output_folder}/{batch["camera_id"]}_{batch["timestamp"]}_{duration}.mp4', fourcc, fps, (frame_width, frame_height))

            for frame_info in frames:
                image_path = frame_info["image_path"]
                frame = cv2.imread(image_path)
                video_writer.write(frame)

            video_writer.release()
            print("Video created successfully.")
        else:
            print("No frames found for the selected batch.")
    except Exception as e:
        error_message = f"Error extracting frames: {str(e)}"
        logging.error(error_message, exc_info = True)

if __name__ == "__main__":
    try:
        available_timestamps_with_cameras = get_available_timestamps_with_cameras()

        if not available_timestamps_with_cameras:
            print("No timestamps available in the database.")
        else:
            print("Available timestamps with respective cameras:")
            for i, timestamp_with_cams in enumerate(available_timestamps_with_cameras, start=1):
                print(f"{i}. {timestamp_with_cams}")

            
            selection = input("Select a timestamp index (enter the number): ")
                
            duration = input("Now enter a duration--(default 60 press enter or escape)")
            if not duration:
                duration = 60
            else:
                duration = int(duration)
            try:
                selected_timestamp = available_timestamps_with_cameras[int(selection) - 1]
                batch_duration = int(config['General']['batch_duration'])

                matching_batch = find_nearest_batch(selected_timestamp, batch_duration)

                if matching_batch:
                    output_folder = "output"
                    os.makedirs(output_folder, exist_ok=True)
                    extract_frames(matching_batch, output_folder, duration)
                else:
                    print("No matching batch found. Please try a different timestamp.")
            except (ValueError, IndexError):
                print("Invalid selection. Please enter a valid number.")
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(error_message, exc_info = True)
