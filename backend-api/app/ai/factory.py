from app.ai.base import AIService
from app.ai.mock_ai import MockAIService
from app.ai.ollama_ai import OllamaAIService
from app.core.config import settings


def get_ai_service() -> AIService:
    if settings.ai_provider == "ollama":
        return OllamaAIService()
    return MockAIService()
