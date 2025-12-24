"""Service for generating animated explanations with audio narration"""

import logging
import json
import base64
import os
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from .heygen_service import HeyGenService

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Generates animated explanations with synchronized audio narration
    Uses OpenAI for both animation structure generation and TTS
    Optionally generates avatar video using HeyGen
    """

    def __init__(self):
        """Initialize explanation service with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
        self.client = AsyncOpenAI(api_key=api_key)

        # Initialize HeyGen service
        self.heygen_service = HeyGenService()
        self.enable_avatar = os.getenv("ENABLE_HEYGEN_AVATAR", "true").lower() == "true"

        logger.info(f"ExplanationService initialized (HeyGen avatar: {self.enable_avatar})")

    async def generate_explanation(
        self,
        answer: str,
        question: str = "",
        generate_avatar: bool = True
    ) -> Optional[Dict]:
        """
        Generate animated explanation with audio from answer text

        Args:
            answer: The answer text to explain with animation
            question: Optional question context for better structuring
            generate_avatar: Whether to generate HeyGen avatar video

        Returns:
            Dict with animation data, audio, and optional video_url
        """
        try:
            # Step 1: Generate animation structure using LLM
            animation_data = await self._generate_animation_structure(answer, question)

            if not animation_data:
                logger.warning("Failed to generate animation structure")
                return None

            # Step 2: Generate audio narration using TTS
            audio_base64 = await self._generate_audio(animation_data["narration"])

            if not audio_base64:
                logger.warning("Failed to generate audio")
                return None

            result = {
                "animation": animation_data,
                "audio": audio_base64,
                "duration": animation_data.get("duration", 10.0)
            }

            # Step 3: Optionally generate avatar video
            if generate_avatar and self.enable_avatar:
                logger.info("🎬 Generating HeyGen avatar video...")
                video_data = self.heygen_service.create_video_from_audio(
                    audio_base64=audio_base64,
                    background="#FFFFFF"
                )

                if video_data:
                    result["avatar_video_url"] = video_data["video_url"]
                    result["avatar_video_id"] = video_data["video_id"]
                    logger.info(f"✅ Avatar video generated: {video_data['video_url']}")
                else:
                    logger.warning("⚠️ Failed to generate avatar video, continuing without it")

            return result

        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}", exc_info=True)
            return None

    async def _generate_animation_structure(
        self,
        answer: str,
        question: str
    ) -> Optional[Dict]:
        """
        Use LLM to structure answer into animated steps with timing

        Returns:
            Dict with narration text and animation steps
        """
        try:
            prompt = f"""Convert this educational answer into an animated explanation structure.

Question: {question if question else "N/A"}
Answer: {answer}

Create a JSON structure with:
1. "narration": Comprehensive spoken explanation that FULLY covers EVERY point in the answer (conversational tone)
2. "steps": Array of animation steps matching narration, each with:
   - "id": unique identifier (step-1, step-2, etc.)
   - "content": Text/visual content to display
   - "startTime": When to show this step (seconds, starting from 0)
   - "duration": How long to display (seconds)
   - "animation": Animation type ("fadeIn", "slideIn", "highlight", "scale", "pulse")

CRITICAL Guidelines:
- The narration MUST explain EVERY statement/point in the answer with sufficient detail
- If the answer has multiple statements (e.g., 6 statements), the narration must address ALL of them
- Make narration natural and conversational for text-to-speech
- Break answer into appropriate steps (typically 1 step per major point/statement)
- Time steps to sync with narration flow - allocate 5-10 seconds per statement
- Use animations that emphasize key points
- Total duration should be adequate for the content (estimate 5-10 seconds per statement/key point)
- For multi-part answers, ensure each part gets adequate narration time

Return ONLY valid JSON, no markdown formatting.

Example output:
{{
  "narration": "Let me explain each of these statements. First, regarding statement one... Second, for statement two... Third...",
  "steps": [
    {{
      "id": "step-1",
      "content": "First key point here",
      "startTime": 0,
      "duration": 5,
      "animation": "fadeIn"
    }}
  ],
  "duration": 30
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content designer. Generate structured animation data for explanations. Always ensure the narration comprehensively covers ALL points in the answer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            animation_data = json.loads(content)

            # Validate structure
            if "narration" not in animation_data or "steps" not in animation_data:
                logger.error("Invalid animation structure: missing required fields")
                return None

            # Calculate duration if not provided
            if "duration" not in animation_data and animation_data["steps"]:
                max_end_time = max(
                    step["startTime"] + step["duration"]
                    for step in animation_data["steps"]
                )
                animation_data["duration"] = max_end_time

            logger.info(f"Generated animation with {len(animation_data['steps'])} steps")
            return animation_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse animation JSON: {str(e)}")
            logger.error(f"Content received: {content}")
            return None
        except Exception as e:
            logger.error(f"Error generating animation structure: {str(e)}", exc_info=True)
            return None

    async def _generate_audio(self, narration_text: str) -> Optional[str]:
        """
        Generate audio narration using OpenAI TTS

        Args:
            narration_text: Text to convert to speech

        Returns:
            Base64 encoded audio data (MP3), or None if generation fails
        """
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",  # Use tts-1-hd for higher quality
                voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
                input=narration_text,
                response_format="mp3"
            )

            # Convert audio bytes to base64 for easy transmission
            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            logger.info(f"Generated audio: {len(audio_bytes)} bytes")
            return audio_base64

        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}", exc_info=True)
            return None

    def should_generate_explanation(self, answer: str, question: str = "") -> bool:
        """
        Determine if an answer warrants an animated explanation

        Criteria:
        - Answer is educational/explanatory in nature
        - Answer is not too short (< 100 chars) or too long (> 3000 chars)
        - Answer contains concepts that benefit from visualization

        Returns:
            True if explanation should be generated
        """
        answer_len = len(answer)

        if not answer or answer_len < 100:
            logger.debug(f"Answer too short: {answer_len} chars")
            return False

        if answer_len > 3000:
            logger.info(f"Answer too long for explanation: {answer_len} chars (max 3000)")
            return False

        # Check for educational keywords
        educational_keywords = [
            "explain", "because", "therefore", "example", "concept",
            "formula", "equation", "theorem", "principle", "process",
            "step", "first", "second", "finally", "result", "means",
            "definition", "understand", "learn", "know"
        ]

        answer_lower = answer.lower()
        keyword_matches = sum(1 for keyword in educational_keywords if keyword in answer_lower)

        if keyword_matches >= 2:
            logger.info(f"✓ Explanation eligible: {answer_len} chars, {keyword_matches} educational keywords")
            return True
        else:
            logger.debug(f"Not enough educational keywords: {keyword_matches}/2 required")
            return False


# Testing
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test():
        service = ExplanationService()

        # Test explanation generation
        question = "What is a prime number?"
        answer = "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself. For example, 2, 3, 5, 7, and 11 are prime numbers. The number 2 is the only even prime number because all other even numbers are divisible by 2."

        logger.info("Generating explanation...")
        result = await service.generate_explanation(answer, question)

        if result:
            logger.info(f"✓ Generated explanation with {len(result['animation']['steps'])} steps")
            logger.info(f"✓ Duration: {result['duration']} seconds")
            logger.info(f"✓ Narration: {result['animation']['narration'][:100]}...")
            logger.info(f"✓ Audio size: {len(result['audio'])} chars (base64)")
        else:
            logger.error("✗ Failed to generate explanation")

    asyncio.run(test())
