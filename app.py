from flask import Flask, render_template, Response
import cv2
import sqlite3

app = Flask(__name__)

# Add the database connection
db_connection = sqlite3.connect('video_analytics.db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/batches')
def batches():
    # Fetch batches from the database
    cursor = db_connection.cursor()
    cursor.execute('SELECT * FROM batches')
    batches = cursor.fetchall()
    return render_template('batches.html', batches=batches)

@app.route('/logs')
def logs():
    # Read and display logs from the log file
    with open('logs.log', 'r') as log_file:
        logs = log_file.readlines()
    return render_template('logs.html', logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
