FROM python:3.14

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
