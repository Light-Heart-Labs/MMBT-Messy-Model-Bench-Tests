FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl jq ca-certificates poppler-utils unzip nano less \
    build-essential \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    fonts-liberation fonts-dejavu graphviz \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    requests beautifulsoup4 lxml pandas numpy openpyxl \
    yfinance sec-edgar-downloader markdown reportlab \
    python-pptx matplotlib plotly kaleido Pillow graphviz \
    pytest pytest-cov ruff
WORKDIR /workspace
RUN git config --global user.email "agent@bench.local" && git config --global user.name "bench-agent"
CMD ["sleep","infinity"]
