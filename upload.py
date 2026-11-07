import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(file_path, title, description):
    credentials = Credentials.from_authorized_user_info(
        json.loads(os.environ["YOUTUBE_TOKEN"]),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    youtube = build("youtube", "v3", credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "20"
            },
            "status": {"privacyStatus": "private"}
        },
        media_body=MediaFileUpload(file_path, mimetype="video/mp4")
    )

    return request.execute()
