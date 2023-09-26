# Video Surveillance System

A multi-threaded video surveillance system for capturing and processing video frames from multiple cameras.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)

## Overview

This project is a multi-threaded video surveillance system that captures video frames from multiple cameras, processes the frames, and stores the frame information and images in a database. The system allows you to perform batch processing of video frames and retrieve video clips for specific time intervals.

## Features

- Multi-threaded frame capture from multiple cameras.
- Real-time processing and storage of video frames.
- Batch processing of video frames with user-defined duration.
- Retrieval of video clips for specific time intervals.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed.
- OpenCV (`cv2`) library installed.
- SQLite database installed (for database functionality).

## Getting Started

To get started with this project, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/video-surveillance-system.git
   cd video-surveillance-system


2. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the system by editing the `config.ini` file.

4. Create the necessary folders:
    (actually created automatiaclly in the code but works the same when created manuallly also)

   ```bash
   mkdir logs images output
   ```

6. Run the video surveillance system:

   ```bash
   python video_surveillance.py
   ```

## Usage

- When you run the system, it will capture frames from the configured cameras, process them, and store them in the `images` folder.
- You can specify a duration to create video clips from the captured frames. The clips will be saved in the `output` folder.
- The system logs frame information to the `logs` folder.

## Configuration

You can configure the system by editing the `config.ini` file. Here are some of the key configurations:

- `batch_duration`: The duration of each batch in seconds.
- `log_file`: The file where log information is saved.
- `log_level`: The log level (e.g., INFO, DEBUG, ERROR).
- `error_log`: error log for the camera_feeds code file. 
- `output_fps`: Frames per second for the output video clips.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.
   
