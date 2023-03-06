FROM ${DOCKER_REGISTRY}python:3.10.9-slim@sha256:3ec369a5db9693672a61f0631a980e66eb6d161f206afa7c9c18237adac466f5 as base_image
WORKDIR /opt

ARG PIP_INDEX_URL
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt --no-cache-dir --no-deps

COPY . .
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
