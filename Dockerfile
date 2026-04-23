FROM python:3.11-slim

WORKDIR /app

# System-Abhängigkeiten für weasyprint
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev libcairo2 cron && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--config", "config/settings.yaml", "--output", "output/report.html"]
