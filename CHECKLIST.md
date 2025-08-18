# Maintainer's Verification Checklist

This checklist should be run by a maintainer after fixing a bug or adding a feature to ensure that core functionality has not been broken.

**Prerequisites:**
-   A stable environment with at least one working camera.
-   All dependencies installed from the corrected `requirements.txt`.
-   The `logs`, `images`, and `output` directories have been cleared.

---

### **1. Backend Data Generation**

-   [ ] **Action:** Run the backend script for at least 2 minutes.
    -   **Command:** `python video_surveillance_backend.py`
-   [ ] **Verification:**
    -   [ ] The script does not hang and prints regular output.
    -   [ ] The `logs/app.log` file is created and contains JSON data.
    -   [ ] The `images/Camera_0/` directory (or equivalent) is created and contains multiple `.jpg` files.
    -   [ ] The `video_analytics.db` file is created.
    -   [ ] **Action:** Terminate the script with Ctrl+C. It should exit cleanly.

### **2. Database Content Verification**

-   [ ] **Action:** Use an SQLite viewer or a script to inspect the database.
-   [ ] **Verification:**
    -   [ ] The `batches` table contains at least one row.
    -   [ ] The `camera_frame_count` table contains at least one row with a `frame_count` greater than 0.

### **3. Video Clip Retrieval**

-   [ ] **Action:** Run the video retrieval program.
    -   **Command:** `python camera_feeds_retrieval_program.py`
-   [ ] **Verification:**
    -   [ ] The script lists available timestamps from the recent backend run.
    -   [ ] **Action:** Select a valid index and duration (e.g., 1 and 10).
    -   [ ] The script prints "Video created successfully."
    -   [ ] The `output/` directory contains a new `.mp4` video file.
    -   [ ] The generated video file is playable and has the correct duration.

### **4. Web Application Basic Functionality**

-   [ ] **Action:** Run the web application.
    -   **Command:** `python app.py`
-   [ ] **Verification:**
    -   [ ] The Flask server starts without errors.
    -   [ ] **Action:** Navigate to `http://127.0.0.1:5000/`. The page loads without errors.
    -   [ ] **Action:** Navigate to `http://127.0.0.1:5000/logs`. The page loads and displays log content.
    -   [ ] **Action:** Navigate to `http://127.0.0.1:5000/batches`. The page loads and displays batch information.
    -   [ ] **(If live feed is implemented)** The main page shows a live video feed without console errors.
