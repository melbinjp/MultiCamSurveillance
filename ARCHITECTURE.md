# Architecture

This document provides a high-level overview of the video surveillance system's architecture.

## Textual Architecture Diagram

The system is composed of two loosely-coupled parts: a backend/CLI for data processing and a non-functional web interface.

### 1. Backend and CLI Data Pipeline

This is the core, functional part of the system.

```
+---------------------------------+
| video_surveillance_backend.py   |  (Main Process)
| - Detects cameras               |
| - Spawns threads per camera     |
+---------------------------------+
      |
      | (Captures frames)
      |
      v
+---------------------------------+
|          Data Stores            |
|---------------------------------|
| 1. images/      (JPG frames)    |
| 2. logs/app.log (JSON metadata) |
| 3. video_analytics.db (SQLite)  |
+---------------------------------+
      ^
      | (Reads all three stores)
      |
+---------------------------------+
| camera_feeds_retrieval_program.py|  (CLI Tool)
| - User selects timestamp        |
| - Reads logs/images/db          |
| - Generates MP4 video           |
+---------------------------------+
      |
      | (Writes video file)
      |
      v
+---------------------------------+
| output/         (MP4 videos)    |
+---------------------------------+
```

### 2. Web Application (Incomplete)

This part of the system is not functional.

```
+---------------------------------+
|           User's Browser        |
+---------------------------------+
      |
      | (HTTP Request to /)
      |
      v
+---------------------------------+
|             app.py              |  (Flask Server)
| - Serves index.html             |
| - (Broken) /logs & /batches     |
| - (Missing) /video_feed endpoint|
+---------------------------------+
      |
      | (Renders template)
      |
      v
+---------------------------------+
|      templates/index.html       |
|      static/js/app.js           |
| - Tries to connect to /video_feed|
+---------------------------------+
```

## File Map

-   `app.py`: **[Web Entry Point]** A Flask web server that is intended to provide a web UI. It is buggy and incomplete.
-   `video_surveillance_backend.py`: **[Backend Entry Point]** The main application logic for detecting cameras, capturing frames, and saving them to disk and database.
-   `camera_feeds_retrieval_program.py`: **[CLI Entry Point]** A command-line tool for generating video clips from the captured data.
-   `config.ini`: **[Configuration]** Stores configuration settings for logging, batch duration, and FPS.
-   `requirements.txt`: **[Dependencies]** Lists the Python dependencies for the project.
-   `video_analytics.db`: **[State]** An SQLite database that stores metadata about processing batches and frame counts.
-   `static/`: **[Web UI]** Contains the JavaScript for the web application.
    -   `js/app.js`: Attempts to connect to a non-existent video streaming endpoint.
-   `templates/`: **[Web UI]** Contains the HTML templates for the Flask application.
    -   `index.html`: The main page, containing an `<img>` tag for the live feed.
-   `images/`: **[Data Store]** The root directory where captured image frames are stored, organized by camera ID.
-   `logs/`: **[Data Store]** The directory where log files are stored.
    -   `app.log`: Contains structured JSON information about each saved frame.
    -   `error.log`: Contains error logs.
-   `output/`: **[Data Store]** The directory where generated MP4 video clips are saved.

## Runtime Assumptions

-   **Python 3.x**: The code is written in Python 3. The exact version is not specified, but updated dependencies require a relatively modern version.
-   **OpenCV**: The system relies heavily on OpenCV (`cv2`) for all video capture and processing tasks. A working OpenCV installation is critical.
-   **Physical Cameras**: The backend assumes that one or more physical video cameras are connected and available to `cv2.VideoCapture()`. The application does not handle the case where no cameras are found and will hang indefinitely.
-   **File System Access**: The application requires read/write access to the current working directory to create the `logs`, `images`, `output` directories, and the `video_analytics.db` file.
-   **Desktop Environment**: The CLI and backend are designed to be run in a standard desktop or server command-line environment. The web application is designed to be accessed by a modern web browser.
