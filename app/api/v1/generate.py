import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.config import get_settings, Settings
from app.schemas.requests import GenerateRequest
from app.schemas.responses import GenerateResponse
from app.services.variation_engine import VariationEngine

router = APIRouter(tags=["Generation"])
logger = logging.getLogger(__name__)

# In-memory job store for caching generation results
job_store: Dict[str, GenerateResponse] = {}

def get_variation_engine(request: Request) -> VariationEngine:
    """Dependency to retrieve VariationEngine from app state."""
    return request.app.state.variation_engine

@router.post("/generate", response_model=GenerateResponse, response_model_exclude_none=True)
async def generate_variations(
    req: GenerateRequest,
    settings: Settings = Depends(get_settings),
    engine: VariationEngine = Depends(get_variation_engine)
):
    """
    Generate question variations based on the given request.
    """
    max_variations = getattr(settings, "max_variations", 100)
    if hasattr(req, "count") and req.count > max_variations:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Requested count {req.count} exceeds maximum allowed ({max_variations})."
        )

    try:
        response = await engine.generate(req)
        
        # Ensure the response has a job_id (generate one if missing)
        job_id = getattr(response, "job_id", None)
        if not job_id:
            import uuid
            job_id = str(uuid.uuid4())
            if hasattr(response, "job_id"):
                response.job_id = job_id
        
        # Store in memory for later export
        job_store[job_id] = response
        
        return response
        
    except ConnectionError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service unavailable")
    except ValueError as e:
        logger.error(f"Validation error in generation: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Internal generation error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
