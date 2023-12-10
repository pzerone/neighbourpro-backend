FROM python:latest
COPY . .
RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade -r  requirements.txt
WORKDIR /app
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]