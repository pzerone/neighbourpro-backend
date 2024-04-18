FROM python:latest
COPY . .
RUN pip install --no-cache-dir --upgrade -r  requirements.txt
WORKDIR Surprise
RUN python3 setup.py install
WORKDIR /
EXPOSE 8000
RUN chmod +x startup.sh
CMD ["./startup.sh", "prod"]
