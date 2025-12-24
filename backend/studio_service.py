"""Studio service for generating educational content"""

import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)


class StudioService:
    """Service for generating educational content like summaries, quizzes, flashcards, and reports"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("StudioService initialized")

    async def generate_summary(self, conversation_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Generate a concise summary of the conversation and key points

        Args:
            conversation_history: List of conversation messages
            session_id: Session identifier

        Returns:
            Dictionary with summary data
        """
        logger.info(f"Generating summary for session {session_id}")

        # Build context from conversation
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on the following conversation, create a comprehensive summary with:
1. Main topics discussed
2. Key concepts explained
3. Important questions asked
4. Learning outcomes

Conversation:
{conversation_text}

Format your response as:
## Main Topics
- List key topics

## Key Concepts
- Explain important concepts

## Questions Explored
- Summarize main questions

## Learning Outcomes
- What was learned
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational assistant creating clear, concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            summary_text = response.choices[0].message.content

            return {
                "type": "summary",
                "session_id": session_id,
                "content": summary_text,
                "message_count": len(conversation_history),
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise

    async def generate_quiz(self, conversation_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Generate multiple-choice quiz questions based on the conversation

        Args:
            conversation_history: List of conversation messages
            session_id: Session identifier

        Returns:
            Dictionary with quiz questions
        """
        logger.info(f"Generating quiz for session {session_id}")

        # Build context from conversation
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on the following educational conversation, create 5 multiple-choice questions to test understanding.

Conversation:
{conversation_text}

For each question, provide:
1. The question text
2. Four answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format as JSON:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational assistant creating quiz questions. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            quiz_data = json.loads(response.choices[0].message.content)

            return {
                "type": "quiz",
                "session_id": session_id,
                "questions": quiz_data.get("questions", []),
                "total_questions": len(quiz_data.get("questions", [])),
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise

    async def generate_flashcards(self, conversation_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Generate flashcards for studying key concepts

        Args:
            conversation_history: List of conversation messages
            session_id: Session identifier

        Returns:
            Dictionary with flashcard data
        """
        logger.info(f"Generating flashcards for session {session_id}")

        # Build context from conversation
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on the following educational conversation, create 8-10 flashcards for studying.

Conversation:
{conversation_text}

Each flashcard should have:
1. A front side (question or term)
2. A back side (answer or definition)

Format as JSON:
{{
  "flashcards": [
    {{
      "front": "What is...?",
      "back": "It is...",
      "category": "Concept name"
    }}
  ]
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational assistant creating study flashcards. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            flashcard_data = json.loads(response.choices[0].message.content)

            return {
                "type": "flashcards",
                "session_id": session_id,
                "flashcards": flashcard_data.get("flashcards", []),
                "total_cards": len(flashcard_data.get("flashcards", [])),
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error generating flashcards: {str(e)}")
            raise

    async def generate_report(self, conversation_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive learning report

        Args:
            conversation_history: List of conversation messages
            session_id: Session identifier

        Returns:
            Dictionary with report data
        """
        logger.info(f"Generating report for session {session_id}")

        # Build context from conversation
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        prompt = f"""Based on the following educational conversation, create a comprehensive learning report with:

1. **Learning Journey Overview**: How the learning progressed
2. **Topics Mastered**: Concepts that were well understood
3. **Areas for Review**: Topics that need more attention
4. **Study Recommendations**: Specific suggestions for further learning
5. **Performance Metrics**: Engagement level, question quality, understanding depth

Conversation:
{conversation_text}

Format your response in clear markdown with sections and bullet points.
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational analyst creating comprehensive learning reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            report_text = response.choices[0].message.content

            return {
                "type": "report",
                "session_id": session_id,
                "content": report_text,
                "message_count": len(conversation_history),
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    async def generate_analyze_map(self, conversation_history: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Generate a hierarchical curriculum/topic map from the conversation.
        Analyzes the educational content and creates a structured tree of topics and subtopics.
        """
        logger.info(f"Generating analyze map for session {session_id}")

        # Build conversation context
        conversation_text = ""
        for msg in conversation_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{role.upper()}: {content}\n\n"

        prompt = f"""Based on the following educational conversation, create a hierarchical curriculum framework
that maps out the main topics and their subtopics discussed.

Analyze the content and identify:
1. The main subject or curriculum area (root topic)
2. Major topics within that subject (level 1)
3. Subtopics and concepts within each major topic (level 2 and beyond)

Create a hierarchical structure that shows how topics are organized and related.

Conversation:
{conversation_text}

Return your response as a JSON object with this exact structure:
{{
  "title": "Main curriculum title (e.g., 'Grade 9 Mathematics Curriculum Framework')",
  "source_count": 1,
  "root_node": {{
    "id": "root",
    "title": "Main subject name",
    "subtopics": [
      {{
        "id": "topic-1",
        "title": "First major topic",
        "subtopics": [
          {{
            "id": "subtopic-1-1",
            "title": "First subtopic",
            "subtopics": []
          }}
        ]
      }}
    ]
  }}
}}

Each node should have a unique id, a descriptive title, and a subtopics array (can be empty).
Base the curriculum structure on the actual content discussed in the conversation.
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an educational curriculum analyzer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            analyze_map_data = json.loads(response.choices[0].message.content)

            return {
                "type": "analyzemap",
                "session_id": session_id,
                **analyze_map_data,
                "timestamp": None
            }

        except Exception as e:
            logger.error(f"Error generating analyze map: {str(e)}")
            raise
