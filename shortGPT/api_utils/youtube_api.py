import os
import json
import subprocess
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secret.json"  # You'll need to create this

def get_authenticated_service():
    """Get authenticated YouTube service using OAuth2."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"⚠️ Failed to load token: {e}")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None
        
        if not creds:
            # Check if we have client_secret.json
            if os.path.exists(CLIENT_SECRETS_FILE):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRETS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("✅ OAuth2 authentication successful")
                except Exception as e:
                    print(f"⚠️ OAuth2 flow failed: {e}")
                    return None
            else:
                print("⚠️ client_secret.json not found. Using cookies.txt fallback...")
                return None
        
        # Save the credentials for the next run
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ Token saved to token.json")
        except Exception as e:
            print(f"⚠️ Failed to save token: {e}")
    
    try:
        return build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"⚠️ Failed to build YouTube service: {e}")
        return None

def upload_to_youtube(video_path, title, description, keywords, privacy_status, token_data=None):
    """
    Upload a video to YouTube using the official YouTube Data API v3.
    """
    print(f"📤 Uploading to YouTube: {video_path}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    # Try OAuth2 with YouTube API first
    youtube = get_authenticated_service()
    
    if youtube:
        try:
            # Build the request body
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': keywords if keywords else [],
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media file upload
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            # Upload the video
            print("📤 Uploading with YouTube API...")
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"📊 Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtu.be/{video_id}"
            print(f"✅ Upload successful: {video_url}")
            return {"success": True, "video_id": video_id, "url": video_url}
            
        except Exception as e:
            print(f"⚠️ YouTube API upload failed: {str(e)}")
    
    # Fallback: Try using yt-dlp with cookies if available
    if os.path.exists("cookies.txt"):
        print("📤 Attempting fallback upload with yt-dlp + cookies...")
        try:
            cmd = [
                "yt-dlp",
                "--cookies", "cookies.txt",
                "--no-check-certificate",
                "--title", title[:100],
                "--description", description[:5000],
                "--privacy", privacy_status,
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                output = result.stdout + result.stderr
                url_match = re.search(r'https://youtu\.be/([a-zA-Z0-9_-]+)', output)
                if url_match:
                    video_id = url_match.group(1)
                    print(f"✅ Upload successful: https://youtu.be/{video_id}")
                    return {"success": True, "video_id": video_id, "url": f"https://youtu.be/{video_id}"}
                else:
                    print("✅ Upload successful (URL not found in output)")
                    return {"success": True, "message": "Upload completed"}
        except Exception as e:
            print(f"⚠️ Fallback upload failed: {e}")
    
    print("❌ All upload methods failed")
    return {"success": False, "error": "Upload failed"}
