from fastapi import APIRouter, HTTPException
import requests
import logging
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/heygen/token")
async def create_heygen_token():
    """Create a HeyGen access token for streaming avatar"""
    try:
        url = "https://api.heygen.com/v1/streaming.create_token"
        headers = {
            "x-api-key": settings.heygen_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("data", {}).get("token"),
                "expires_at": data.get("data", {}).get("expires_at")
            }
        else:
            logger.error(f"HeyGen token creation failed: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create HeyGen token: {response.text}"
            )
            
    except requests.RequestException as e:
        logger.error(f"Request error creating HeyGen token: {e}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating HeyGen token: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/heygen/avatars")
async def list_avatars():
    """List available HeyGen avatars"""
    try:
        url = "https://api.heygen.com/v2/avatars"
        headers = {
            "x-api-key": settings.heygen_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to list avatars: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to list avatars: {response.text}"
            )
            
    except requests.RequestException as e:
        logger.error(f"Request error listing avatars: {e}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error listing avatars: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/heygen/voices") 
async def list_voices():
    """List available HeyGen voices"""
    try:
        url = "https://api.heygen.com/v2/voices"
        headers = {
            "x-api-key": settings.heygen_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to list voices: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to list voices: {response.text}"
            )
            
    except requests.RequestException as e:
        logger.error(f"Request error listing voices: {e}")
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error listing voices: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/heygen/config")
async def get_heygen_config():
    """Get HeyGen configuration for frontend"""
    return {
        "avatar_id": settings.heygen_avatar_id,
        "voice_id": settings.heygen_voice_id
    } 