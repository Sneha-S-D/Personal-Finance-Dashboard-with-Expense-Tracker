FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

# Gunicorn will run your Flask `server` from main.py
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "main:server"]
