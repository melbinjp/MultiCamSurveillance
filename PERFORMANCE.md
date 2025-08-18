# Performance Analysis

This document provides an analysis of the application's performance characteristics based on code inspection. Live performance metrics could not be measured due to the application not being fully functional in the test environment.

## Measured Metrics (Not Performed)

-   **FPS (Frames Per Second):** NOT MEASURED. The backend could not be run with a live camera feed.
-   **Load Time:** NOT MEASURED. The web application is not fully functional.
-   **Memory Usage:** NOT MEASURED.

**Reason:** The primary backend script (`video_surveillance_backend.py`) could not be run to completion as it hangs when no cameras are detected. The video generation script (`camera_feeds_retrieval_program.py`) fails to write its output file due to an environmental issue. Therefore, no meaningful performance metrics could be gathered.

## Bottleneck Analysis and Suggestions

### 1. Log File Parsing in `camera_feeds_retrieval_program.py`

-   **Observation:** **[MEDIUM]** The `extract_frames` function reads the entire log file (`logs/app.log`) into memory for each execution.
    ```python
    with open(log_file, 'r') as log:
        for line in log:
            # ... parsing logic ...
    ```
-   **Bottleneck:** As the system runs for an extended period, the log file could grow to be very large (gigabytes). Reading the entire file into memory and processing it line-by-line to find a small subset of frames will become extremely slow and memory-intensive.
-   **Suggestion:** The system should use the SQLite database more effectively. The `batches` table already stores the start and end frame IDs. The `extract_frames` function should first query the database to get the exact range of frames it needs. The log file should then be used only as a lookup for the image path, and even this could be optimized by storing the image path directly in the database.

### 2. Frame Saving in `video_surveillance_backend.py`

-   **Observation:** **[LOW]** The `process_and_save_frames` function writes one frame per second to disk as a JPG image using `cv2.imwrite()`.
    ```python
    if frame_id % fps == 0:
        # ...
        image_path = os.path.join(camera_folder, f"frame_{frame_id}.jpg")
        cv2.imwrite(image_path, frame)
    ```
-   **Bottleneck:** `cv2.imwrite()` is a blocking I/O operation. For a system with many cameras running at a high resolution, the overhead of encoding and writing a JPG file for each camera every second could become a performance bottleneck, potentially causing frames to be dropped.
-   **Suggestion:** Consider using a separate, dedicated thread pool for writing images to disk. This would offload the I/O operation from the main frame capture and processing thread, making the capture loop more resilient to I/O latency.

### 3. Lack of Lazy Loading / Pagination in Web UI

-   **Observation:** **[LOW]** The `/batches` endpoint in `app.py` fetches all batch records from the database at once.
    ```python
    cursor.execute('SELECT * FROM batches')
    batches = cursor.fetchall()
    ```
-   **Bottleneck:** While not currently a problem, if the system were to run for a long time, the `batches` table could contain thousands or millions of entries. Fetching and rendering all of them at once would make the `/batches` page extremely slow or unusable.
-   **Suggestion:** Implement pagination for all data-listing endpoints in the web application. The API should accept `page` and `limit` parameters to only fetch and display a subset of the data at a time.
