# Dependencies and Environment

This document details the project's dependencies, environment setup, and the commands required to run the application.

## Dependencies

The project's Python dependencies are listed in `requirements.txt`.

### Original `requirements.txt`

The `requirements.txt` file as provided in the repository is as follows:

```
opencv-python==4.5.3.56
numpy==1.19.5
configparser
```

**[LOW]** These pinned versions are outdated and were found to be incompatible with modern Python environments (Python 3.12), causing installation to fail.

### Modified `requirements.txt`

To successfully install the dependencies, the version pins were removed. The following content was used for a successful installation:

```
opencv-python
numpy
configparser
```

**[HIGH]** This modification allowed for a successful installation of the latest compatible versions of the libraries.

### Dependency Audit

A security audit was performed on the installed dependencies using `pip-audit`.

```
$ pip-audit
No known vulnerabilities found
```

**[HIGH]** The installed dependencies have no known vulnerabilities at the time of this audit.

## Build & Run Commands

The following sections describe the commands to run the different components of the application and their observed behavior on a fresh clone.

### 1. Install Dependencies

**Command:**
```bash
# First, modify requirements.txt as described above.
pip install -r requirements.txt
```

**Observed Behavior:**
**[HIGH]** The command successfully installs all necessary dependencies. The original `requirements.txt` fails to install.

### 2. Run the Backend Frame Capture

**Command:**
```bash
python video_surveillance_backend.py
```

**Observed Behavior:**
**[HIGH]** The script hangs indefinitely if no physical cameras are detected. It does not provide any error message or exit gracefully. It must be manually terminated. This is a critical bug. In the process, it creates the `logs` and `images` directories but does not create any log files.

**Error Log (Timeout):**
```
The command timed out after 402.4154603481293 seconds. If you intended to run a background task, use `&` next time. If you are running tests, tailor the test command to run just the affected tests. The next command will start a new bash session, losing environment variables and other state.
```

### 3. Run the Video Retrieval Program

This program requires data to be present (logs, images, and a database). The backend's failure to run prevents this data from being generated. To test this script, dummy data was created manually.

**Command (with interactive input):**
```bash
# The script prompts for a timestamp index and a duration.
# Here, we select the first available timestamp and a 5-second duration.
echo -e "1\n5" | python camera_feeds_retrieval_program.py
```

**Observed Behavior:**
**[MEDIUM]** The script successfully reads the dummy log data, finds the corresponding dummy image files, and reports that the video was created successfully. However, **no output file is actually generated**. This appears to be a silent error related to the execution environment, as multiple bugs in the script's logic were fixed, and the script now has valid inputs.

**Observed Output:**
```
Available timestamps with respective cameras:
1. ('2024-08-17 12:00:00', 'Camera_0')
Select a timestamp index (enter the number): Now enter a duration--(default 60 press enter or escape)5 frames has been retrieved
Image Width: 640 pixels
Image Height: 480 pixels
Video created successfully.
```

### 4. Run the Web Application

**Command:**
```bash
python app.py
```

**Observed Behavior:**
**[HIGH]** The Flask application starts successfully in debug mode. However, it is non-functional and has several critical bugs that will be detailed in the `BUGS_AND_ISSUES` report. Accessing the `/logs` endpoint, for example, will cause the application to crash due to a `FileNotFoundError`. The main page loads but the video feed is broken as it points to an unimplemented backend endpoint.
