import dropbox
import json
from flask import Flask, render_template, request, jsonify
import requests
import logging
import uuid

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Dropbox API credentials
APP_KEY = 'kpq58myzzjnd1e4'
APP_SECRET = 'zv4f67ifjm2rfk2'
REFRESH_TOKEN = 'NuUSJFQdOEgAAAAAAAAAAWa1D0x5kJJvl-0XWMOofnbbQonvCDKD2sQ0TDGg678X'

# Function to refresh Dropbox access token
def refresh_access_token(refresh_token, client_id, client_secret):
    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, data=data)

    if response.status_code == 200:
        new_tokens = response.json()
        access_token = new_tokens['access_token']
        logging.info("New Access Token retrieved.")
        return access_token
    else:
        logging.error("Failed to refresh access token: %s", response.text)
        return None

# Refresh Dropbox access token
DROPBOX_ACCESS_TOKEN = refresh_access_token(REFRESH_TOKEN, APP_KEY, APP_SECRET)
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Store course codes in memory
course_codes = {}

@app.route('/')
def home():
    return render_template('login.html')  # Default to login page

@app.route('/signup.html')
def signup():
    return render_template('signup.html')  # Route for signup page

@app.route('/index.html')
def index():
    return render_template('index.html')  # Route for the dashboard

@app.route('/upload', methods=['POST'])
def upload():
    video_file = request.files['video']
    course_data = json.loads(request.form.get('courseData'))

    # Extract course information
    course_name = course_data["Course name"]  # This is case-sensitive
    course_author = course_data["Course Author"]
    video_title = video_file.filename

    # Generate or retrieve course code
    course_code = course_codes.get(course_name)  # Case-sensitive lookup
    if course_code is None:
        # Generate a unique course code
        course_code = str(uuid.uuid4())  # Generate a unique code
        course_codes[course_name] = course_code  # Store in memory with case sensitivity

    # Define paths in Dropbox
    video_path = f'/UPLOAD/{video_title}'  # Save videos directly in UPLOAD folder
    course_json_path = f'/UPLOAD/{video_title.split(".")[0]}.json'  # JSON file path named after video

    # Check if course JSON exists
    existing_course_data = {}
    try:
        dbx.files_get_metadata(course_json_path)  # Only check existence
        # If the file exists, download and update it
        _, res = dbx.files_download(course_json_path)
        existing_course_data = json.loads(res.content)
        
        # Append new video title to the video list
        existing_course_data["Video list"].append(video_title)
    except dropbox.exceptions.ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            # If course JSON doesn't exist, create a new course data structure
            existing_course_data = {
                "Course name": course_name,
                "Course code": course_code,
                "Course Author": course_author,
                "Video list": [video_title]  # Start the list with the first video title
            }
        else:
            logging.error("Failed to check course JSON: %s", e)
            return jsonify({'message': 'Failed to check course JSON.'}), 500

    # Upload the video file to Dropbox using requests
    try:
        upload_url = "https://content.dropboxapi.com/2/files/upload"
        headers = {
            "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
            "Dropbox-API-Arg": json.dumps({
                "path": video_path,
                "mode": "add",  # Or "overwrite" if you want to replace existing files
                "mute": True
            }),
            "Content-Type": "application/octet-stream"
        }

        # Stream the video file in chunks
        response = requests.post(upload_url, headers=headers, data=video_file.stream, timeout=900)  # 15 minutes

        if response.status_code == 200:
            logging.info(f"Uploaded video: {video_path}")
        else:
            logging.error("Failed to upload video: %s", response.text)
            return jsonify({'message': f'Failed to upload video: {response.text}'}), 500

    except Exception as e:
        logging.error("Failed to upload video: %s", str(e))
        return jsonify({'message': f'Failed to upload video: {str(e)}'}), 500

    # Update or create the course JSON file in Dropbox
    try:
        dbx.files_upload(
            json.dumps(existing_course_data).encode('utf-8'), 
            course_json_path, 
            mode=dropbox.files.WriteMode.overwrite  # Overwrite with updated video list
        )
        logging.info(f"Updated course JSON: {course_json_path}")
        return jsonify({'message': 'Video and course data uploaded successfully!'}), 200
    except Exception as e:
        logging.error("Failed to save course data: %s", str(e))
        return jsonify({'message': f'Failed to save course data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
