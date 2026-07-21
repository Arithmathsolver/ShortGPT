import os
import sys
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
        try:
            for f in os.listdir('.'):
                print(f"  - {f}")
        except Exception as e:
            print(f"  Error listing files: {e}")
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
        try:
            for f in os.listdir('.'):
                print(f"  - {f}")
        except Exception as e:
            print(f"  Error listing files: {e}")
        # Check if videos directory exists
        if os.path.exists('videos'):
            print("📁 Contents of videos/ directory:")
            try:
                for f in os.listdir('videos'):
                    print(f"  - {f}")
            except Exception as e:
                print(f"  Error listing videos: {e}")
        return {"success": False, "error": f"Video file not found: {video_path}"}
    
    # Check file size
    file_size = os.path.getsize(video_path)
    print(f"📊 File
