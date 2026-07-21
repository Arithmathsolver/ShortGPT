import os
import json
import subprocess
import re
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# YouTube upload scope
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Get authenticated YouTube service using Service Account (works headless)."""
    print("🔐 Checking for service account credentials...")
    
    # Check for service account credentials
    if os.path.exists('service_account.json'):
        try:
            print("📄 Found service_account.json, loading...")
            creds = service_account.Credentials.from_service_account_file(
                'service_account.json', scopes=SCOPES)
            print("✅ Loaded service account credentials")
            return build('youtube', 'v3', credentials=creds)
        except Exception as e:
            print(f"⚠️ Failed to load service account: {e}")
            return None
    else:
        print("⚠️ service_account.json not found!")
        # List files in current directory for debugging
        print("📁 Files in current directory:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        return None

def upload_to_youtube(video_path, title, description, keywords, privacy_status, token_data=None):
    """
    Upload a video to YouTube using Service Account authentication (headless).
    """
    print("=" * 60)
    print("📤 STARTING YOUTUBE UPLOAD PROCESS")
    print("=" * 60)
    
    print(f"📁 Video path received: '{video_path}'")
    print(f"📝 Title: {title if title else 'Not provided'}")
    print(f"🔒 Privacy: {privacy_status if privacy_status else 'Not provided'}")
    
    # Debug: Check if video_path is None or empty
    if video_path is None:
        print("❌ ERROR: video_path is None")
        print("💡 Debug: The video path was not passed correctly to the function")
        return {"success": False, "error": "Video path is None"}
    
    if not video_path:
        print("❌ ERROR: video_path is empty string")
        print("💡 Debug: The video path was an empty string")
        return {"success": False, "error": "Video path is empty"}
    
    # Convert to string and strip
    video_path = str(video_path).strip()
    print(f"📁 Cleaned video path: '{video_path}'")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        print("📁 Current directory contents:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        # Check if videos directory exists
        if os.path.exists('videos'):
            print("📁 Contents of videos/ directory:")
            for f in os.listdir('videos'):
                print(f"  - {f}")
        return {"success": False, "error": f"Video file not found: {video_path}"}
    
    # Check file size
    file_size = os.path.getsize(video_path)
    print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
    
    # Get authenticated service
    youtube = get_authenticated_service()
    
    if not youtube:
        print("❌ Failed to authenticate with YouTube API")
        return {"success": False, "error": "Authentication failed"}
    
    try:
        # Build the request body
        body = {
            'snippet': {
                'title': title[:100] if title else "Untitled Video",  # YouTube title limit
                'description': description[:5000] if description else "",  # YouTube description limit
                'tags': keywords if keywords else [],
                'categoryId': '22'  # People & Blogs category
            },
            'status': {
                'privacyStatus': privacy_status if privacy_status else 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media file upload
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        # Upload the video
        print("📤 Uploading with YouTube API (Service Account)...")
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        last_progress = 0
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                if progress - last_progress >= 10:
                    print(f"📊 Upload progress: {progress}%")
                    last_progress = progress
        
        video_id = response['id']
        video_url = f"https://youtu.be/{video_id}"
        print(f"✅ Upload successful: {video_url}")
        return {"success": True, "video_id": video_id, "url": video_url}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Upload failed: {error_msg}")
        
        if "quota" in error_msg.lower():
            print("💡 YouTube API quota exceeded. Check your quota limits.")
        elif "auth" in error_msg.lower():
            print("💡 Authentication error. Check service account permissions.")
        elif "permission" in error_msg.lower():
            print("💡 Permission error. Make sure service account is invited as Manager in YouTube Studio.")
        
        return {"success": False, "error": error_msg}
