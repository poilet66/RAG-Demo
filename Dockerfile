FROM python:3.9-slim

# Install build dependencies and curl
RUN apt-get update && apt-get install -y \
   build-essential \
   python3-dev \
   curl \
   && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Setup app directory
WORKDIR /app

# Copy pyproject and sourcecode
COPY pyproject.toml ./
COPY src/ ./src/

# Install ChromaDB using UV
RUN uv sync