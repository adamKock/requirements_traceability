FROM python:3.12-slim

WORKDIR /app

ENV HF_HOME=/app/.cache/huggingface

# Copy only requirements first, so this layer is cached unless deps change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models — cached unless requirements.txt changes
RUN python3 -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('all-mpnet-base-v2'); \
CrossEncoder('cross-encoder/stsb-roberta-base')"
ENV HF_HOME=/opt/hf_cache

# Copy the rest of your code LAST — changes here don't bust the model cache
COPY . .

EXPOSE 8000
CMD ["python", "main.py"]