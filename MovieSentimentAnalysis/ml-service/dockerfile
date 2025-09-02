FROM python:3.11-slim-bookworm

# Create non-root user
#RUN groupadd -r mluser && useradd -r -g mluser mluser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Download NLTK data as root user (before switching to mluser)
RUN python -c "import nltk; nltk.download('punkt', quiet=True)" && \
    python -c "import nltk; nltk.download('stopwords', quiet=True)" && \
    echo "NLTK data downloaded successfully" || echo "NLTK download failed"

# Copy ML service code
COPY app.py .
COPY preprocessing.py .
COPY train_model.py .
COPY model/ ./model/
COPY . .
# Create necessary directories and fix permissions
RUN mkdir -p /app/model \
    && chown -R mluser:mluser /app \
    && chmod -R 755 /root/nltk_data 2>/dev/null || true


# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "app.py"]