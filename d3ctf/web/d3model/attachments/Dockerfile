FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY index.html .

ENV FLAG=${FLAG:-flag{test}}

EXPOSE 5000

CMD ["python", "app.py"]