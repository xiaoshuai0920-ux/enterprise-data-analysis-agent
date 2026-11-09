FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /app/data
ENV PYTHONPATH=/app
CMD ["sh", "-c", "python -m app.scripts.seed_demo && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
