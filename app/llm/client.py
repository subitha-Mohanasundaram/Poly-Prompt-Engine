import asyncio
import logging
import time
from typing import Tuple, Optional

try:
    import ollama
except ImportError:
    ollama = None

logger = logging.getLogger(__name__)

class OllamaClient:
    """Async Ollama client wrapper for local LLM inference."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.base_url = base_url
        self.model = model
        if ollama is not None:
            self.client = ollama.AsyncClient(host=base_url)
        else:
            self.client = None
            logger.warning("ollama package is not installed.")
        logger.info(f"Initialized OllamaClient with model={model}, host={base_url}")
        
    async def generate_structured(self, prompt: str, schema: dict, temperature: float = 0.7) -> str:
        """
        Generate a structured JSON response from the LLM.
        Uses ollama's format=schema capability for grammar-constrained generation.
        """
        if self.client is None:
            raise RuntimeError("Ollama package is not installed or client is uninitialized.")

        max_retries = 3
        backoff_factor = 1.5
        
        prompt_len = len(prompt)
        logger.debug(f"Sending prompt of length {prompt_len} to {self.model}")
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = await self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    format=schema,
                    options={"temperature": temperature, "num_predict": 4096}
                )
                duration = time.time() - start_time
                content = response["message"]["content"]
                logger.info(f"LLM request completed in {duration:.2f}s. Response length: {len(content)}")
                return content
                
            except Exception as e:
                logger.warning(f"Ollama generation failed on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached for Ollama generation.")
                    raise
                await asyncio.sleep(backoff_factor ** attempt)
                
        raise RuntimeError("Failed to generate structured output")

    async def check_health(self) -> Tuple[bool, str]:
        """Check if the Ollama service is reachable."""
        if self.client is None:
            return False, "Ollama client uninitialized"
        try:
            response = await self.client.list()
            models = [m.get("name", "unknown") for m in response.get("models", [])]
            return True, f"Ollama is reachable. Models: {', '.join(models)}"
        except Exception as e:
            return False, f"Ollama health check failed: {e}"

    async def ensure_model_available(self) -> bool:
        """Ensure the configured model is available locally."""
        if self.client is None:
            return False
        try:
            response = await self.client.list()
            models = [m.get("name") for m in response.get("models", [])]
            if any(self.model in m for m in models if m):
                return True
            logger.warning(f"Model {self.model} not found in available models: {models}")
            return False
        except Exception as e:
            logger.error(f"Failed to check available models: {e}")
            return False
