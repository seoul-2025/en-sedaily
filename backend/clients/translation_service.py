"""
Translation Service
Handles text translation using Anthropic Claude API
"""
import httpx
from typing import List, Optional
import logging
import os
import boto3
import json

logger = logging.getLogger(__name__)


def get_anthropic_api_key() -> str:
    """
    Get Anthropic API key from AWS Secrets Manager or environment variable

    Priority:
    1. ANTHROPIC_API_KEY environment variable
    2. AWS Secrets Manager (en-translate secret)
    3. Fallback to empty string

    Returns:
        API key string
    """
    # Try environment variable first
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        logger.info("Using ANTHROPIC_API_KEY from environment variable")
        return api_key

    # Try Secrets Manager
    try:
        secret_name = os.environ.get('SECRET_NAME', 'en-translate')
        region = os.environ.get('AWS_REGION', 'us-east-1')

        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region)

        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']

        logger.info(f"Using API key from Secrets Manager: {secret_name}")
        return secret
    except Exception as e:
        logger.error(f"Failed to retrieve API key from Secrets Manager: {e}")
        return ""


class TranslationError(Exception):
    """Raised when translation fails"""
    pass


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class TranslationService:
    """
    Service for translating text using Anthropic Claude
    Handles single and batch translations
    """
    
    def __init__(
        self,
        model_id: str = "claude-opus-4.5-20250514",
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialize Translation Service

        Args:
            model_id: Claude model ID
            region: Unused (kept for compatibility)
            aws_access_key_id: Unused (kept for compatibility)
            aws_secret_access_key: Unused (kept for compatibility)
            anthropic_api_key: Anthropic API key (if not provided, will try env var or Secrets Manager)
        """
        self.model_id = model_id or "claude-opus-4-5-20251101"
        # Get API key: priority = parameter > env var > Secrets Manager
        self.api_key = anthropic_api_key or get_anthropic_api_key()
        if not self.api_key:
            logger.warning("No Anthropic API key configured. Translations will fail.")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _validate_text(self, text: str) -> None:
        """
        Validate that text is non-empty and not just whitespace
        
        Args:
            text: Text to validate
        
        Raises:
            ValidationError: If text is empty or whitespace-only
        """
        if not text or not text.strip():
            raise ValidationError("Translation text must be non-empty and not just whitespace")
    
    def _load_translation_prompt(self) -> str:
        """
        Load translation prompt from TRANSLATION_PROMPT.md
        
        Returns:
            System prompt for translation
        """
        import os
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "TRANSLATION_PROMPT.md")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load TRANSLATION_PROMPT.md: {e}. Using default prompt.")
            return """You are a professional translator for Seoul Economic Daily. Translate Korean business news articles to English in the style of WSJ, FT, Reuters, and Bloomberg.

Key principles:
1. Maintain factual accuracy - never add information not in the original
2. Use active voice and concise sentences (max 40 words)
3. Follow inverted pyramid structure
4. Preserve quotes exactly (no paraphrasing)
5. Include proper nouns in English (company names, person names)

Output format:
[HEADLINE] (10 words max, present tense)
[BYLINE] By [Reporter Name]
[ARTICLE] (translated article body)
[DISCLAIMER] This article was automatically translated from Korean using AI. For accuracy, please refer to the original article."""
    
    async def translate(
        self,
        text: str,
        source_lang: str = "ko",
        target_lang: str = "en",
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        Translate a single text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: "ko" for Korean)
            target_lang: Target language code (default: "en" for English)
            custom_prompt: Optional custom translation prompt
        
        Returns:
            Translated text
        
        Raises:
            ValidationError: If input validation fails
            TranslationError: If translation fails
        """
        self._validate_text(text)
        
        # Load system prompt from file
        system_prompt = self._load_translation_prompt()
        
        # User message
        user_message = f"Translate the following Korean article to English:\n\n{text}"
        
        try:
            response = await self.client.post(
                self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model_id,
                    "max_tokens": 8192,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_message}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()

            # Validate response structure
            if not data.get("content"):
                logger.error(f"Empty content in API response: {data}")
                raise TranslationError("Translation failed: Empty content in API response")

            if len(data["content"]) == 0:
                logger.error(f"No content blocks in API response: {data}")
                raise TranslationError("Translation failed: No content blocks in API response")

            if not data["content"][0].get("text"):
                logger.error(f"No text in content block: {data['content'][0]}")
                raise TranslationError("Translation failed: No text in content block")

            return data["content"][0]["text"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API error: {e.response.status_code} - {e.response.text}")
            raise TranslationError(f"Translation failed: HTTP {e.response.status_code}")
        except KeyError as e:
            logger.error(f"Translation response parse error: {str(e)}, data: {data if 'data' in locals() else 'N/A'}")
            raise TranslationError(f"Translation failed: Invalid response format - {str(e)}")
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise TranslationError(f"Translation failed: {str(e)}")
    
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "ko",
        target_lang: str = "en",
        custom_prompt: Optional[str] = None
    ) -> List[str]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code (default: "ko" for Korean)
            target_lang: Target language code (default: "en" for English)
            custom_prompt: Optional custom translation prompt
        
        Returns:
            List of translated texts in the same order as input
        
        Raises:
            ValidationError: If input validation fails
            TranslationError: If translation fails
        """
        if not texts:
            return []
        
        # Validate all texts
        for i, text in enumerate(texts):
            try:
                self._validate_text(text)
            except ValidationError as e:
                raise ValidationError(f"Text at index {i} is invalid: {str(e)}")
        
        # Translate each text individually
        translations = []
        for text in texts:
            translated = await self.translate(text, source_lang, target_lang, custom_prompt)
            translations.append(translated)
        
        return translations

    async def generate_ai_summary(
        self,
        title: str,
        content: str
    ) -> dict:
        """
        Generate AI summary for an article

        Args:
            title: Article title (English)
            content: Article content (English)

        Returns:
            Dictionary with 'summary' and 'key_points' keys

        Raises:
            TranslationError: If summary generation fails
        """
        try:
            # Limit content to first 3000 characters
            content_excerpt = content[:3000] if len(content) > 3000 else content

            prompt = f"""You are a professional news editor. Create a concise AI summary for this article.

Article Title: {title}

Article Content:
{content_excerpt}

Please provide:
1. A 2-3 sentence summary that captures the main points
2. Exactly 3 key points that readers should know

Format your response as JSON:
{{
  "summary": "2-3 sentence summary here",
  "key_points": [
    "First key point",
    "Second key point",
    "Third key point"
  ]
}}

Keep the summary factual, neutral, and focused on the most important information."""

            response = await self.client.post(
                self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model_id,
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            if not data.get("content") or len(data["content"]) == 0:
                logger.error(f"Empty content in AI summary response: {data}")
                raise TranslationError("AI summary generation failed: Empty content")

            response_text = data["content"][0].get("text", "")

            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                summary_data = json.loads(json_match.group(0))
            else:
                summary_data = json.loads(response_text)

            # Validate response format
            if "summary" not in summary_data or "key_points" not in summary_data:
                logger.error(f"Invalid AI summary format: {summary_data}")
                raise TranslationError("AI summary generation failed: Invalid format")

            if not isinstance(summary_data["key_points"], list):
                logger.error(f"key_points is not a list: {summary_data}")
                raise TranslationError("AI summary generation failed: key_points must be a list")

            logger.info(f"Generated AI summary successfully")
            return summary_data

        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API error during summary generation: {e.response.status_code} - {e.response.text}")
            raise TranslationError(f"AI summary generation failed: HTTP {e.response.status_code}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI summary JSON: {str(e)}, response: {response_text if 'response_text' in locals() else 'N/A'}")
            raise TranslationError(f"AI summary generation failed: Invalid JSON - {str(e)}")
        except Exception as e:
            logger.error(f"AI summary generation error: {str(e)}")
            raise TranslationError(f"AI summary generation failed: {str(e)}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

