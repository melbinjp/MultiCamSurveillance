# Issue: Backend hangs indefinitely if no cameras are found

-   **Severity:** High
-   **Confidence:** [HIGH]
-   **Status:** Confirmed

## Description

The main backend script, `video_surveillance_backend.py`, is responsible for detecting and capturing frames from connected cameras. If the script is run in an environment with no cameras available, it enters an infinite loop and hangs indefinitely, consuming CPU resources without providing any output or error message.

## Reproduction

1.  Run the backend script on a machine with no webcams or accessible video devices: `python video_surveillance_backend.py`

## Expected vs. Actual Behavior

-   **Expected:** The application should detect that no cameras are available, print a clear error message to the console (e.g., "No cameras found. Exiting."), and terminate gracefully.
-   **Actual:** The application provides no output and the process hangs, requiring a manual kill command (e.g., Ctrl+C) to terminate.

## Root Cause

**File:** `video_surveillance_backend.py`
**Lines:** 178-180 and the `check_available_cameras` function.
**Code:**
```python
# The camera_check_thread runs this loop, which may hang inside VideoCapture
def check_available_cameras(interval=5):
    global available_camera_ids
    while True:
        camera_ids = []
        camera_id = 0
        while True:
            cap = cv2.VideoCapture(camera_id) # This call can hang
            if not cap.isOpened():
                break
            camera_ids.append(camera_id)
            cap.release()
            camera_id += 1
        available_camera_ids = camera_ids
        time.sleep(interval)

# The main thread runs this loop, waiting for the list to be populated
while True:
    active_camera_ids = available_camera_ids
    print(len(active_camera_ids))
    # ...
```
The `cv2.VideoCapture(camera_id)` call can block for a long time on some systems if the camera index is invalid or no cameras are present. The main loop of the script prints the number of cameras but never gets a chance to run if the camera check thread is permanently blocked.

## Suggested Patch

The camera detection logic should be made more robust. It should have a timeout, and the main application should have a startup check that exits if no cameras are found after a reasonable period.

**Code Sketch (`check_available_cameras`):**
A simple improvement is to add a limit to how many camera indices it checks.
```python
def check_available_cameras(interval=5, max_cameras_to_check=10):
    global available_camera_ids
    while True:
        camera_ids = []
        # Check only a reasonable number of camera indices
        for camera_id in range(max_cameras_to_check):
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                camera_ids.append(camera_id)
                cap.release()
        available_camera_ids = camera_ids
        time.sleep(interval)
```

**Code Sketch (Main Loop):**
The main loop should check if cameras are found and print a message if not.
```python
# In the main script body, after starting the check thread
print("Searching for cameras...")
time.sleep(6) # Give the check thread a moment to run

if not available_camera_ids:
    print("No cameras found after 6 seconds. Exiting.")
    exit()

print(f"Found {len(available_camera_ids)} cameras. Starting main loop.")
while True:
    # ... existing main loop logic ...
```

## Tests to Add

-   A startup test should be created that runs the backend in an environment with no cameras and asserts that it exits gracefully within a few seconds.
