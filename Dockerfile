FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app
COPY src /app/
COPY requirements.txt /app/requirements.txt
RUN pip install -q -r /app/requirements.txt
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]