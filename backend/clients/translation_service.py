"""
Translation Service
Handles text translation using Anthropic Claude API
"""
import httpx
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


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
            anthropic_api_key: Anthropic API key
        """
        self.model_id = model_id or "claude-opus-4-5-20251101"
        self.api_key = anthropic_api_key or "your_anthropic_api_key_here"
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
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

