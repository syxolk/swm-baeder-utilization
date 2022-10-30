FROM python:3.9.0-slim
RUN pip3 install requests
WORKDIR /app
COPY organizations.json .
COPY crawler.py .
CMD ["python3", "crawler.py", "organizations.json", "/app/data"]
