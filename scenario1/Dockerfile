# Stage 1: build dependencies (builder)
FROM python:3.10-slim AS builder

WORKDIR /app


# Copy only requirements first to leverage cache
COPY requirements.txt .


# Install dependencies into a virtual location
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# Stage 2: runtime image
FROM python:3.10-slim

WORKDIR /app


# Copy installed packages from builder
COPY --from=builder /install /usr/local


# Copy only application code (now this layer changes often — placed after deps)
COPY main.py .


ENV PATH=/usr/local/bin:$PATH


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]