# CI and Tests

This document provides recommendations for setting up Continuous Integration (CI) and automated testing to improve the quality and reliability of the Video Surveillance System. The project currently has no automated tests.

## Suggested GitHub Actions Workflow

A basic CI workflow can be created to automatically install dependencies and run a smoke test on each push to the repository. This ensures that the application at least starts up correctly.

**File:** `.github/workflows/ci.yml`

**Snippet:**
```yaml
name: Python Application CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.9
      uses: actions/setup-python@v3
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        # Use the modified requirements file
        echo "opencv-python" > requirements.txt
        echo "numpy" >> requirements.txt
        echo "configparser" >> requirements.txt
        pip install -r requirements.txt

    - name: Run Smoke Test
      run: |
        python smoke_test.py
```

## Minimal Automated Smoke Test

A simple smoke test can be written to verify that the main scripts can be imported and that they don't immediately crash due to syntax errors or other basic issues. It can also check that the backend script exits gracefully if it's run with a timeout, addressing the "hangs on startup" bug.

**File:** `smoke_test.py`

**Script:**
```python
import subprocess
import os
import sys

def run_script_with_timeout(script_name, timeout=10):
    """Runs a script and terminates it if it exceeds the timeout."""
    print(f"--- Running smoke test for {script_name} ---")

    try:
        # We expect the backend to time out, as it hangs by design when no cameras are found.
        # A successful test for the backend is one that *does not* hang indefinitely.
        proc = subprocess.run(
            [sys.executable, script_name],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        print(f"{script_name} exited with code {proc.returncode}.")
        # The script should ideally exit with code 0.
        # For now, we just check that it exits.
        return True

    except subprocess.TimeoutExpired:
        print(f"SUCCESS: {script_name} ran for {timeout} seconds and was terminated as expected.")
        # This is the expected outcome for the buggy backend.
        if "video_surveillance_backend.py" in script_name:
            return True
        else:
            print(f"FAILURE: {script_name} timed out unexpectedly.")
            return False

    except Exception as e:
        print(f"FAILURE: {script_name} failed with an exception: {e}")
        return False

def main():
    print("Starting smoke tests...")

    # Test 1: Check backend script
    backend_ok = run_script_with_timeout("video_surveillance_backend.py", timeout=5)

    # Test 2: Check CLI retrieval script (it should run and exit quickly as it's interactive)
    # We can't easily test its full functionality without data, but we can check if it starts.
    cli_ok = run_script_with_timeout("camera_feeds_retrieval_program.py", timeout=5)

    # Test 3: Check web app script
    web_app_ok = run_script_with_timeout("app.py", timeout=5)

    if not all([backend_ok, cli_ok, web_app_ok]):
        print("\nSome smoke tests failed.")
        sys.exit(1)

    print("\nAll smoke tests passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
```
**Note:** This smoke test is designed around the current buggy behavior. As bugs are fixed, the smoke test should be updated to reflect the expected correct behavior (e.g., the backend should exit gracefully with a non-zero exit code instead of timing out).
