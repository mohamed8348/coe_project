FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# In a real scenario, you'd copy requirements.txt and install
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# Mocking pip install for typical packages
RUN pip install --no-cache-dir fastapi uvicorn pydantic pandas scikit-learn psycopg2-binary

# Copy source code
COPY src/ /app/src/
COPY api/ /app/api/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
