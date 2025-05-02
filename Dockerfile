FROM python:3.10-slim

# System dependencies (git sometimes required for model loading)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install -r requirements.txt

# Expose API port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

