import dropbox
from flask import Flask, request, jsonify, render_template
import requests

APP_KEY = 'kpq58myzzjnd1e4'
APP_SECRET = 'zv4f67ifjm2rfk2'
REFRESH_TOKEN = 'NuUSJFQdOEgAAAAAAAAAAWa1D0x5kJJvl-0XWMOofnbbQonvCDKD2sQ0TDGg678X'

# Function to refresh the Dropbox access token using refresh token
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
        print("New Access Token:", access_token)
        return access_token
    else:
        print("Failed to refresh access token:", response.text)
        return None

app = Flask(__name__)

# Refresh the access token
DROPBOX_ACCESS_TOKEN = refresh_access_token(REFRESH_TOKEN, APP_KEY, APP_SECRET)

# Initialize Dropbox with the refreshed access token
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def create_folder_if_not_exists(folder_path):
    """
    Check if the folder exists in Dropbox. If not, create it.
    """
    try:
        dbx.files_get_metadata(folder_path)
    except dropbox.exceptions.ApiError as e:
        if isinstance(e.error, dropbox.files.GetMetadataError) and e.error.get_path().is_not_found():
            dbx.files_create_folder_v2(folder_path)

@app.route('/')
def index():
    # Render the HTML form
    return render_template('index.html')

@app.route('/upload-video', methods=['POST'])
def upload_video():
    # Get the uploaded video from the form
    video_file = request.files['videoFile']
    
    # Dropbox folder path to store the uploaded videos
    folder_path = '/UPLOAD'
    video_path = f'{folder_path}/{video_file.filename}'

    try:
        # Ensure the folder exists or create it
        create_folder_if_not_exists(folder_path)
        
        # Upload the video file to Dropbox
        dbx.files_upload(video_file.read(), video_path, mute=True)
        return jsonify({'message': 'Video uploaded successfully!'})

    except Exception as e:
        return jsonify({'message': f'Failed to upload: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
