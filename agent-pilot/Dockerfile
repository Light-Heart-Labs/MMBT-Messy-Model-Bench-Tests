FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl jq ca-certificates poppler-utils unzip nano less \
    build-essential \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir requests beautifulsoup4 lxml pandas numpy openpyxl yfinance sec-edgar-downloader markdown reportlab
WORKDIR /workspace
RUN git config --global user.email "agent@bench.local" && git config --global user.name "bench-agent"
CMD ["sleep","infinity"]
