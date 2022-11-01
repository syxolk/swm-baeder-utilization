FROM python:3.9.0-slim
RUN pip3 install seaborn pandas matplotlib tqdm pytz Jinja2
WORKDIR /app
COPY ./templates/ templates/
COPY ./static/ static/
COPY renderer.py .
CMD ["python3", "renderer.py", "/app/data", "/app/out"]
