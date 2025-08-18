# Issue: Fragile log parsing for video retrieval

-   **Severity:** Medium
-   **Confidence:** [HIGH]
-   **Status:** Identified

## Description

The `camera_feeds_retrieval_program.py` script works by reading the `logs/app.log` file line by line to find the JSON metadata for each frame. However, the method it uses to extract the JSON object is highly fragile. It assumes that every log line will have a specific format and that the JSON object can be found by splitting the string at the first `{` character.

## Root Cause

**File:** `camera_feeds_retrieval_program.py`
**Line:** 103
**Code:**
```python
# Split the line at the first occurrence of "{"
parts = line.split("{", 1)
if len(parts) > 1:
    # Extract the JSON portion (everything after the first "{")
    json_data = "{" + parts[1]
    frame_info = json.loads(json_data)
```
This approach is brittle for several reasons:
1.  If the logging format changes (e.g., the timestamp or log level includes a `{` character for some reason), the parsing will fail.
2.  If a log message that is *not* a frame metadata entry is logged to the same file and happens to contain a `{`, the script might try (and fail) to parse it as JSON.
3.  It prevents the use of more advanced, structured logging formats (like logging pure JSON objects) because it relies on this specific string manipulation.

## Suggested Patch

Instead of this fragile parsing, the system should log the frame metadata as a clean JSON string on its own, and the retrieval program should be simplified to parse each line directly as a JSON object.

**Suggested Logging Change (`video_surveillance_backend.py`):**
```python
# In process_and_save_frames():
frame_json = json.dumps(frame_info)
# Instead of logging.info(frame_json), which prepends date/time,
# use a dedicated logger that only outputs the message.
# Or, more simply, write directly to a dedicated data file.
with open("frame_data.log", "a") as f:
    f.write(frame_json + "\n")
```

**Suggested Retrieval Change (`camera_feeds_retrieval_program.py`):**
```python
# In extract_frames():
with open("frame_data.log", 'r') as log:
    for line in log:
        try:
            frame_info = json.loads(line)
            # ... proceed with filtering logic ...
        except json.JSONDecodeError:
            continue
```
This approach decouples the application's diagnostic logs from its data output, making the system more robust and maintainable.

## Tests to Add

-   A unit test for the log parsing/data extraction logic should be added to ensure it can handle various valid and invalid line formats.
