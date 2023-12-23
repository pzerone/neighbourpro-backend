FROM python:latest
COPY . .
RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade -r  requirements.txt
EXPOSE 8000
RUN chmod +x startup.sh
CMD ["./startup.sh"]