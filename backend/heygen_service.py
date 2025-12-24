"""
HeyGen API Integration Service
Generates avatar videos from audio
"""

import os
import requests
import logging
import time
import base64
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class HeyGenService:
    """Service for generating avatar videos using HeyGen API"""

    def __init__(self):
        self.api_key = os.getenv("HEYGEN_API_KEY")
        if not self.api_key:
            logger.warning("HEYGEN_API_KEY not found in environment variables")

        self.base_url = "https://api.heygen.com/v2"
        self.avatar_id = os.getenv("HEYGEN_AVATAR_ID", "Anna_public_3_20240108")  # Default avatar
        self.voice_id = os.getenv("HEYGEN_VOICE_ID", "1bd001e7e50f421d891986aad5158bc8")  # Default voice

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_video_from_audio(
        self,
        audio_base64: str,
        background: str = "#FFFFFF"
    ) -> Optional[Dict[str, Any]]:
        """
        Create avatar video from audio

        Args:
            audio_base64: Base64 encoded audio (MP3)
            background: Background color (hex)

        Returns:
            Dict with video_id and video_url, or None if failed
        """
        if not self.api_key:
            logger.error("HeyGen API key not configured")
            return None

        try:
            # Step 1: Create video generation request
            logger.info("Creating HeyGen video generation request...")

            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": self.avatar_id,
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "type": "audio",
                            "audio_url": f"data:audio/mp3;base64,{audio_base64}"
                        },
                        "background": {
                            "type": "color",
                            "value": background
                        }
                    }
                ],
                "dimension": {
                    "width": 720,
                    "height": 1280
                },
                "aspect_ratio": "9:16"
            }

            response = requests.post(
                f"{self.base_url}/video/generate",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"HeyGen API error: {response.status_code} - {response.text}")
                return None

            result = response.json()
            video_id = result.get("data", {}).get("video_id")

            if not video_id:
                logger.error("No video_id returned from HeyGen")
                return None

            logger.info(f"Video generation started. Video ID: {video_id}")

            # Step 2: Poll for video status
            video_url = self._wait_for_video(video_id)

            if video_url:
                return {
                    "video_id": video_id,
                    "video_url": video_url
                }

            return None

        except Exception as e:
            logger.error(f"Error creating HeyGen video: {str(e)}", exc_info=True)
            return None

    def _wait_for_video(
        self,
        video_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 5
    ) -> Optional[str]:
        """
        Poll HeyGen API until video is ready

        Args:
            video_id: Video ID to check
            max_wait_seconds: Maximum time to wait
            poll_interval: Seconds between polls

        Returns:
            Video URL if ready, None if timeout or error
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            try:
                response = requests.get(
                    f"{self.base_url}/video/status",
                    headers=self._get_headers(),
                    params={"video_id": video_id},
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    status = result.get("data", {}).get("status")

                    if status == "completed":
                        video_url = result.get("data", {}).get("video_url")
                        logger.info(f"Video ready: {video_url}")
                        return video_url

                    elif status == "failed":
                        logger.error("HeyGen video generation failed")
                        return None

                    elif status in ["pending", "processing"]:
                        logger.info(f"Video status: {status}, waiting...")
                        time.sleep(poll_interval)
                        continue

                else:
                    logger.warning(f"Status check failed: {response.status_code}")
                    time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error checking video status: {str(e)}")
                time.sleep(poll_interval)

        logger.error(f"Video generation timeout after {max_wait_seconds}s")
        return None

    def create_video_from_text(
        self,
        text: str,
        voice_id: Optional[str] = None,
        background: str = "#FFFFFF"
    ) -> Optional[Dict[str, Any]]:
        """
        Create avatar video from text (HeyGen will do TTS)

        Args:
            text: Text to speak
            voice_id: Voice ID (uses default if not provided)
            background: Background color

        Returns:
            Dict with video_id and video_url, or None if failed
        """
        if not self.api_key:
            logger.error("HeyGen API key not configured")
            return None

        try:
            voice_id = voice_id or self.voice_id

            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": self.avatar_id,
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "type": "text",
                            "input_text": text,
                            "voice_id": voice_id
                        },
                        "background": {
                            "type": "color",
                            "value": background
                        }
                    }
                ],
                "dimension": {
                    "width": 720,
                    "height": 1280
                },
                "aspect_ratio": "9:16"
            }

            response = requests.post(
                f"{self.base_url}/video/generate",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"HeyGen API error: {response.status_code} - {response.text}")
                return None

            result = response.json()
            video_id = result.get("data", {}).get("video_id")

            if not video_id:
                logger.error("No video_id returned from HeyGen")
                return None

            logger.info(f"Video generation started. Video ID: {video_id}")

            video_url = self._wait_for_video(video_id)

            if video_url:
                return {
                    "video_id": video_id,
                    "video_url": video_url
                }

            return None

        except Exception as e:
            logger.error(f"Error creating HeyGen video: {str(e)}", exc_info=True)
            return None
