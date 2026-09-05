"""
Poly Prompt Engine — FastAPI application factory.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from app.config import get_settings
from app.llm.client import OllamaClient
from app.utils.embeddings import EmbeddingService
from app.services.duplicate_detector import DuplicateDetector
from app.services.difficulty_validator import DifficultyValidator
from app.services.review_queue import ReviewQueueService
from app.services.variation_engine import VariationEngine
from app.api.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and tear down services."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    logger.info("Starting up Poly Prompt Engine...")

    # --- Initialize services ---
    ollama_client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
    embedding_service = EmbeddingService(model_name=settings.embedding_model)
    duplicate_detector = DuplicateDetector(
        embedding_service=embedding_service,
        threshold=settings.duplicate_similarity_threshold,
    )
    difficulty_validator = DifficultyValidator(llm_client=ollama_client)
    review_queue_service = ReviewQueueService(
        low_confidence_threshold=settings.low_confidence_threshold,
    )
    variation_engine = VariationEngine(
        llm_client=ollama_client,
        duplicate_detector=duplicate_detector,
        difficulty_validator=difficulty_validator,
        review_queue_service=review_queue_service,
        settings=settings,
    )

    # Store in app state for dependency injection
    app.state.ollama_client = ollama_client
    app.state.embedding_service = embedding_service
    app.state.variation_engine = variation_engine
    app.state.settings = settings

    logger.info("All services initialized.")
    yield

    # Shutdown
    logger.info("Shutting down Poly Prompt Engine...")


app = FastAPI(
    title="Poly Prompt Engine",
    description=(
        "Assignment Question Iteration & Variation Generation System. "
        "Generates domain-aware question variations from a seed question "
        "using local open-weight LLMs. National Hackathon 2026 — PS-8."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware — allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API docs."""
    return RedirectResponse(url="/docs")


def run():
    """Entry point for running the application via CLI."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
