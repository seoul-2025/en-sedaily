#!/usr/bin/env python3
"""
Test Anthropic API Connection
Quick test to verify Claude API is working
"""
import asyncio
from clients.translation_service import TranslationService
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_translation():
    """Test Anthropic Claude translation"""
    
    # Sample Korean text
    test_text = """삼성전자가 4분기 영업이익 6조5000억원을 기록했다고 8일 공시했다. 
이는 전년 동기 대비 78% 증가한 수치다."""
    
    logger.info("=" * 60)
    logger.info("Testing Anthropic Claude API Connection")
    logger.info("=" * 60)
    logger.info(f"Model: {settings.anthropic_model_id}")
    logger.info(f"API Key: {settings.anthropic_api_key[:20]}...")
    logger.info("")
    logger.info("Original Korean Text:")
    logger.info(test_text)
    logger.info("")
    
    try:
        # Initialize translation service
        translation_service = TranslationService(
            model_id=settings.anthropic_model_id,
            anthropic_api_key=settings.anthropic_api_key
        )
        
        logger.info("Translating...")
        
        # Translate
        translated = await translation_service.translate(test_text)
        
        logger.info("")
        logger.info("✅ Translation Successful!")
        logger.info("=" * 60)
        logger.info("Translated English Text:")
        logger.info(translated)
        logger.info("=" * 60)
        
        # Close client
        await translation_service.close()
        
        return True
        
    except Exception as e:
        logger.error("")
        logger.error("❌ Translation Failed!")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 60)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_translation())
    exit(0 if success else 1)
