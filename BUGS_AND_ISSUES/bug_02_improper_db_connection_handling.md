# Bug: Improper SQLite database connection handling in Flask app

-   **Severity:** Medium
-   **Confidence:** [HIGH]
-   **Status:** Confirmed

## Description

The Flask web application (`app.py`) creates a single SQLite database connection object at the module level. This is problematic in a multi-threaded web server environment like Flask's default. A single connection object cannot be safely shared across threads for concurrent requests. Furthermore, the connection is never closed, which can lead to resource leaks.

## Reproduction

1.  Inspect the code in `app.py`.
2.  Run the web application: `python app.py`.
3.  While not easily reproducible with simple browsing, this architectural flaw would cause unpredictable errors under concurrent load.

## Expected vs. Actual Behavior

-   **Expected:** The Flask application should manage database connections on a per-request basis, ensuring that each request has its own connection that is properly closed after the request is complete.
-   **Actual:** A single, global connection object is created and shared, which is not safe for concurrent use.

## Root Cause

**File:** `app.py`
**Lines:** 5 and 12
**Code:**
```python
from flask import Flask, render_template, Response
import cv2
import sqlite3

app = Flask(__name__)

# Add the database connection
db_connection = sqlite3.connect('video_analytics.db') #<-- Problem 1: Global connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/batches')
def batches():
    # Fetch batches from the database
    cursor = db_connection.cursor() #<-- Problem 2: Uses global connection
    cursor.execute('SELECT * FROM batches')
    batches = cursor.fetchall()
    return render_template('batches.html', batches=batches)
```

## Suggested Patch

The database connection should be created and torn down within the application context for each request. Flask provides patterns for this.

**Suggested Code:**
```python
import sqlite3
from flask import g

DATABASE = 'video_analytics.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/batches')
def batches():
    # Fetch batches from the database
    cursor = get_db().cursor()
    cursor.execute('SELECT * FROM batches')
    batches = cursor.fetchall()
    # Note: A template for 'batches.html' is missing.
    return render_template('batches.html', batches=batches)
```

## Tests to Add

-   Integration tests for all database-accessing endpoints should be added to ensure they function correctly with the new connection management scheme.
-   (Optional) A load test could be used to verify that the application remains stable under concurrent requests.
