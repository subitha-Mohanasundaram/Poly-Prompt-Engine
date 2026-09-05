import logging
import httpx
from fastapi import APIRouter, Depends
from app.config import get_settings, Settings
from app.schemas.responses import HealthResponse
from app.utils.embeddings import EmbeddingService

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Check the health of the API, Ollama connection, and Embedding Service.
    """
    ollama_connected = False
    try:
        async with httpx.AsyncClient() as client:
            ollama_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
            response = await client.get(f"{ollama_url}/api/tags", timeout=3.0)
            if response.status_code == 200:
                ollama_connected = True
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")

    embedding_service = EmbeddingService(model_name=settings.embedding_model)
    embedding_loaded = embedding_service.is_available()

    if ollama_connected and embedding_loaded:
        status = "healthy"
    elif ollama_connected or embedding_loaded:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        ollama_connected=ollama_connected,
        model_loaded=settings.ollama_model if ollama_connected else "none",
        embedding_model_loaded=embedding_loaded,
        version="1.0.0"
    )
