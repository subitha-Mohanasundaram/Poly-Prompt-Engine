# Model Card for Poly Prompt Engine

## System Purpose
The Poly Prompt Engine is a question variation generation system designed for National Hackathon 2026. It leverages local large language models to generate diverse, high-quality variations of seed questions while maintaining semantic difficulty and preventing duplicates.

## Models Used

| Model | Purpose | Details |
|---|---|---|
| `qwen2.5:7b` | Text Generation | Generates diverse question variations based on seed questions, ensuring domain alignment and cognitive level variations. |
| `all-MiniLM-L6-v2` | Embeddings | Generates sentence embeddings for cosine similarity checks to detect and prevent duplicate questions. |

## Techniques
- **Structured JSON Output**: Enforces specific schemas for the generated outputs to ensure consistency and parsability.
- **Cosine Deduplication**: Uses sentence transformers to compute embeddings and cosine similarity to filter out redundant variations.
- **Batched Inference**: Processes generation requests in batches to optimize throughput and performance.
- **Difficulty Validation**: Ensures generated variations conform to the target difficulty levels (Easy, Medium, Hard).

## Performance
- **Target**: Generate 60 variations in under 5 minutes.
- **Throughput**: Optimized for batching and local inference on GPU-enabled hardware.

## Limitations
- Performance is heavily dependent on the hardware running the local Ollama instance.
- Deduplication relies on embedding similarity, which might occasionally flag semantically similar but conceptually distinct questions as duplicates.
- The `qwen2.5:7b` model may occasionally hallucinate or output non-compliant JSON if the system prompt is overly complex.

## Ethical Considerations
- Ensure that the generated questions do not contain biased, offensive, or inappropriate content.
- The system should be monitored to prevent the generation of harmful instructions.

## License
All models and tools used (Qwen2.5, all-MiniLM-L6-v2, FastAPI, etc.) are available under open-source licenses, primarily Apache 2.0.
