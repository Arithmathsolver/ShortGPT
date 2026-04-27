# shortGPT/utils/__init__.py

import os

def set_api_key(service_name: str, key: str):
    """
    Store API keys for different services in environment variables.
    
    Example:
        set_api_key("GEMINI", "your_key_here")
        set_api_key("PEXELS", "your_key_here")
    """
    if not key:
        raise ValueError(f"❌ Missing API key for {service_name}")
    os.environ[f"{service_name}_API_KEY"] = key
