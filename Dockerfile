FROM python:3.12-slim
RUN useradd -m botuser
USER botuser
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
