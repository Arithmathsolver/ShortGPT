import os
import json
import subprocess
import re
from datetime import datetime

def upload_to_youtube(video_path, title, description, keywords, privacy_status, token_data):
    """
    Upload a video to YouTube using yt-dlp with multiple authentication methods.
    Returns: dict with success status and video URL if successful.
    """
    print(f"📤 Starting YouTube upload process...")
    print(f"📁 Video file: {video_path}")
    print(f"📝 Title: {title}")
    print(f"🔒 Privacy: {privacy_status}")
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return {"success": False, "error": "Video file not found"}
    
    # Build the description with keywords
    full_description = description
    if keywords:
        full_description += f"\n\n{' '.join(['#' + k for k in keywords])}"
    
    # Method 1: Try using cookies.txt
    if os.path.exists("cookies.txt"):
        print("📤 Attempting upload with cookies.txt...")
        cmd = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "--no-check-certificate",
            "--title", title,
            "--description", full_description,
            "--privacy", privacy_status,
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                # Try to extract video URL
                url_match = re.search(r'https://youtu\.be/([a-zA-Z0-9_-]+)', output)
                if url_match:
                    video_id = url_match.group(1)
                    url = f"https://youtu.be/{video_id}"
                    print(f"✅ Upload successful: {url}")
                    return {"success": True, "video_id": video_id, "url": url}
                else:
                    print("✅ Upload successful (but URL not found in output)")
                    return {"success": True, "message": "Upload completed"}
            else:
                print(f"⚠️ Cookie upload failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
        except subprocess.TimeoutExpired:
            print("⚠️ Cookie upload timed out")
        except Exception as e:
            print(f"⚠️ Cookie upload error: {str(e)}")
    
    # Method 2: Try OAuth2 authentication
    print("📤 Attempting upload with OAuth2...")
    cmd = [
        "yt-dlp",
        "--username", "oauth2",
        "--password", "",
        "--no-check-certificate",
        "--title", title,
        "--description", full_description,
        "--privacy", privacy_status,
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            url_match = re.search(r'https://youtu\.be/([a-zA-Z0-9_-]+)', output)
            if url_match:
                video_id = url_match.group(1)
                url = f"https://youtu.be/{video_id}"
                print(f"✅ Upload successful: {url}")
                return {"success": True, "video_id": video_id, "url": url}
            else:
                print("✅ Upload successful (but URL not found in output)")
                return {"success": True, "message": "Upload completed"}
        else:
            print(f"⚠️ OAuth2 upload failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
    except subprocess.TimeoutExpired:
        print("⚠️ OAuth2 upload timed out")
    except Exception as e:
        print(f"⚠️ OAuth2 upload error: {str(e)}")
    
    # Method 3: Try no authentication (will likely fail for private uploads)
    print("📤 Attempting upload with no authentication...")
    cmd = [
        "yt-dlp",
        "--no-check-certificate",
        "--title", title,
        "--description", full_description,
        "--privacy", privacy_status,
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            url_match = re.search(r'https://youtu\.be/([a-zA-Z0-9_-]+)', output)
            if url_match:
                video_id = url_match.group(1)
                url = f"https://youtu.be/{video_id}"
                print(f"✅ Upload successful: {url}")
                return {"success": True, "video_id": video_id, "url": url}
            else:
                print("✅ Upload successful (but URL not found in output)")
                return {"success": True, "message": "Upload completed"}
    except Exception as e:
        print(f"⚠️ No-auth upload error: {str(e)}")
    
    # All methods failed
    print("❌ All upload methods failed")
    print(f"💡 Video saved locally at: {video_path}")
    return {"success": False, "error": "All upload methods failed"}
