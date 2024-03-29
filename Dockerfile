FROM python:3.7.4-alpine3.9
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src src

CMD ["python", "src/main.py"]
