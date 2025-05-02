from fastapi import FastAPI, Request, Header, Query
from fastapi.responses import JSONResponse
from transformers import pipeline
from typing import Dict, Tuple, Optional, List, Any
import asyncio

app = FastAPI()

# Cache format: (task, model_name) → pipeline instance
model_cache: Dict[Tuple[str, str], Any] = {}

# Models to preload at startup (task, model_name)
PRELOAD_MODELS: List[Tuple[str, str]] = [
    ("text-generation", "gpt2"),
    ("text-classification", "protectai/deberta-v3-base-prompt-injection-v2"),
]

GPU_DEVICE = 1  # Reserve device 0 for Ollama


from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer

def try_pipeline(task: str, model_name: str):
    try:
        print(f"[LOAD] Trying {model_name} with device_map='auto'")
        return pipeline(task, model=model_name, device_map="auto")
    except Exception as e:
        print(f"[ERROR] Failed to load {model_name} with device_map='auto': {e}")
        raise e


@app.on_event("startup")
async def preload_models():
    async def load_model(task: str, model_name: str):
        key = (task, model_name)
        if key not in model_cache:
            try:
                pipe = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: try_pipeline(task, model_name)
                )
                model_cache[key] = pipe
                print(f"[READY] {model_name} ({task}) loaded")
            except Exception as e:
                print(f"[ERROR] Failed to preload {model_name} ({task}): {e}")

    await asyncio.gather(*(load_model(task, model) for task, model in PRELOAD_MODELS))


@app.get("/models")
async def list_models():
    return {
        "preloaded": [
            {"task": task, "model": model}
            for (task, model) in model_cache.keys()
        ]
    }


@app.get("/schema")
async def schema(task: Optional[str] = Query(None)):
    """Return example input formats for supported tasks."""
    TASK_SCHEMAS = {
        "text-generation": {
            "prompt": "Once upon a time"
        },
        "text-classification": {
            "prompt": "This is amazing!"
        },
        "question-answering": {
            "prompt": {
                "question": "What is the capital of France?",
                "context": "France is a country in Europe. Its capital is Paris."
            }
        },
        "summarization": {
            "prompt": "Text: The industrial revolution changed the world by..."
        },
        "translation": {
            "prompt": "Translate this sentence to French: The cat is on the table."
        },
        "ner": {
            "prompt": "Hugging Face is based in Paris."
        }
    }

    if task:
        if task not in TASK_SCHEMAS:
            return JSONResponse(status_code=404, content={"error": f"Unknown task: {task}"})
        return {"task": task, "schema": TASK_SCHEMAS[task]}
    else:
        return {"supported_tasks": list(TASK_SCHEMAS.keys())}


@app.post("/huggingface")
async def infer(
    request: Request,
    x_model: Optional[str] = Header(None),
    x_task: Optional[str] = Header("text-generation")
):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body."})

    model_name = x_model or body.get("model")
    task = x_task or body.get("task", "text-generation")
    prompt = body.get("prompt", "")

    if not model_name:
        return JSONResponse(status_code=400, content={"error": "Model name required via header or body."})

    key = (task, model_name)

    if key not in model_cache:
        try:
            print(f"[DYNAMIC LOAD] {model_name} ({task}) not cached, loading...")
            pipe = await asyncio.get_event_loop().run_in_executor(
                None, lambda: try_pipeline(task, model_name)
            )
            model_cache[key] = pipe
            print(f"[CACHED] {model_name} ({task}) now ready")
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Model load failed: {str(e)}"})

    try:
        pipe = model_cache[key]
        result = pipe(prompt)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Inference failed: {str(e)}"})

