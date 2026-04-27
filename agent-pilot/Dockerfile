FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl jq ca-certificates poppler-utils unzip nano less \
    build-essential \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
    fonts-liberation fonts-dejavu graphviz \
 && rm -rf /var/lib/apt/lists/*

# Docker CLI as a static binary (debian's docker.io package doesn't ship /usr/bin/docker
# on bookworm-slim — only dockerd. We just need the client to talk to a mounted host socket).
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.3.1.tgz \
      -o /tmp/docker.tgz \
 && tar xzf /tmp/docker.tgz -C /tmp \
 && mv /tmp/docker/docker /usr/local/bin/docker \
 && rm -rf /tmp/docker /tmp/docker.tgz \
 && docker --version

# GitHub CLI from the official apt repo (added for the DreamServer PR-audit task,
# which auths to api.github.com and would blow the 60 req/hr unauth ceiling otherwise).
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
 && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
 && apt-get update && apt-get install -y --no-install-recommends gh \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir \
    requests beautifulsoup4 lxml pandas numpy openpyxl \
    yfinance sec-edgar-downloader markdown reportlab \
    python-pptx matplotlib plotly kaleido Pillow graphviz \
    pytest pytest-cov ruff
WORKDIR /workspace
RUN git config --global user.email "agent@bench.local" && git config --global user.name "bench-agent"
CMD ["sleep","infinity"]
