# Hugging Face Inference API

This project provides a FastAPI-based API for performing inference using Hugging Face's Transformers library. It supports various NLP tasks such as text generation, text classification, question answering, summarization, translation, and named entity recognition (NER). The API allows dynamic loading and caching of models to optimize performance.

## Features

- **Dynamic Model Loading**: Loads and caches Hugging Face models on-demand or preloads specified models at startup.
- **Task Support**: Supports multiple NLP tasks with appropriate input schemas.
- **GPU Acceleration**: Utilizes `device_map='auto'` for automatic GPU/CPU placement.
- **Asynchronous Processing**: Handles model loading and inference asynchronously for better performance.
- **Model Caching**: Stores loaded models in memory to reduce load times for repeated requests.
- **Schema Endpoint**: Provides example input formats for supported tasks.

## Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Transformers (Hugging Face)
- PyTorch
- A system with GPU support (optional but recommended for performance)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn transformers torch
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. The API will be available at `http://localhost:8000`. Preloaded models (`gpt2` for text generation and `protectai/deberta-v3-base-prompt-injection-v2` for text classification) will be loaded on startup.

### Endpoints

#### 1. List Preloaded Models
- **Endpoint**: `GET /models`
- **Description**: Returns a list of preloaded models and their associated tasks.
- **Example Response**:
  ```json
  {
    "preloaded": [
      {"task": "text-generation", "model": "gpt2"},
      {"task": "text-classification", "model": "protectai/deberta-v3-base-prompt-injection-v2"}
    ]
  }
  ```

#### 2. Get Task Schema
- **Endpoint**: `GET /schema?task={task_name}`
- **Description**: Returns the input schema for a specific task or a list of supported tasks if no task is specified.
- **Example Request**:
  ```bash
  curl http://localhost:8000/schema?task=text-generation
  ```
- **Example Response**:
  ```json
  {
    "task": "text-generation",
    "schema": {
      "prompt": "Once upon a time"
    }
  }
  ```

#### 3. Perform Inference
- **Endpoint**: `POST /huggingface`
- **Description**: Performs inference using the specified model and task.
- **Headers**:
  - `x-model`: Model name (e.g., `gpt2`). Optional if provided in the body.
  - `x-task`: Task type (e.g., `text-generation`). Defaults to `text-generation` if not provided.
- **Body**:
  ```json
  {
    "model": "gpt2",
    "task": "text-generation",
    "prompt": "Once upon a time"
  }
  ```
- **Example Request**:
  ```bash
  curl -X POST http://localhost:8000/huggingface \
  -H "Content-Type: application/json" \
  -H "x-model: gpt2" \
  -H "x-task: text-generation" \
  -d '{"prompt": "Once upon a time"}'
  ```
- **Example Response**:
  ```json
  [
    {
      "generated_text": "Once upon a time, there was a..."
    }
  ]
  ```

### Supported Tasks

- `text-generation`
- `text-classification`
- `question-answering`
- `summarization`
- `translation`
- `ner`

## Configuration

- **Preloaded Models**: Modify the `PRELOAD_MODELS` list in the code to change which models are loaded at startup.
- **GPU Device**: Adjust `GPU_DEVICE` to specify which GPU to use (default is device 1 to reserve device 0 for other processes like Ollama).

## Notes

- Ensure sufficient memory and GPU resources are available when loading large models.
- Models are cached in memory to improve performance for repeated requests.
- If a requested model is not cached, it will be dynamically loaded, which may introduce a delay for the first request.
- Error handling is implemented to provide meaningful error messages for invalid inputs or failed model loading/inference.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
