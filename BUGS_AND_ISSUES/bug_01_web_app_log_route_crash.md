# Bug: Web app crashes when accessing the /logs route

-   **Severity:** High
-   **Confidence:** [HIGH]
-   **Status:** Confirmed

## Description

The Flask web application (`app.py`) has a route `/logs` that is intended to display the contents of the application log. However, it attempts to open a file named `logs.log` which does not exist. The correct log file, as defined in `config.ini`, is `logs/app.log`.

## Reproduction

1.  Run the web application: `python app.py`
2.  Navigate to `http://127.0.0.1:5000/logs` in a web browser.

## Expected vs. Actual Behavior

-   **Expected:** The page should display the contents of the `logs/app.log` file.
-   **Actual:** The application crashes and returns a `500 Internal Server Error`. The console running the Flask app shows a `FileNotFoundError`.

## Root Cause

**File:** `app.py`
**Line:** 22
**Code:**
```python
@app.route('/logs')
def logs():
    # Read and display logs from the log file
    with open('logs.log', 'r') as log_file: #<-- This path is incorrect
        logs = log_file.readlines()
    return render_template('logs.html', logs=logs)
```
The hardcoded path `logs.log` does not match the configured log path `logs/app.log`.

## Suggested Patch

The code should be modified to use the correct path to the log file, ideally by reading it from the `config.ini` file, just as the backend scripts do.

**Simple Fix (Hardcoded):**
```diff
--- a/app.py
+++ b/app.py
@@ -21,7 +21,7 @@
 @app.route('/logs')
 def logs():
     # Read and display logs from the log file
-    with open('logs.log', 'r') as log_file:
+    with open('logs/app.log', 'r') as log_file:
         logs = log_file.readlines()
     return render_template('logs.html', logs=logs)
```

## Tests to Add

-   An integration test should be added for the `/logs` endpoint to ensure it returns a `200 OK` status code and contains expected log content.
