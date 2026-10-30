FROM node:22-bookworm-slim

# Where skills live inside the container
ARG SKILLS_DIR=/skills

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_PATH=/usr/local/lib/node_modules

# System packages: Python, LibreOffice (headless), Poppler (pdftoppm), fonts
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv \
      ca-certificates \
      libreoffice-impress libreoffice-writer libreoffice-calc \
      poppler-utils \
      fonts-liberation fonts-dejavu-core fonts-noto-core fonts-noto-color-emoji \
 && ln -sf /usr/bin/python3 /usr/local/bin/python \
 && fc-cache -f \
 && rm -rf /var/lib/apt/lists/*

# Node side
RUN npm install -g pptxgenjs \
 && npm cache clean --force

# Python side (skill dependencies, plus python-pptx and pandas as optional extras)
RUN pip install \
      "markitdown[pptx]" \
      pillow \
      defusedxml \
      lxml \
      python-pptx \
      pandas

# Skills: copied last so editing a skill only rebuilds this layer
COPY skills/ ${SKILLS_DIR}/
RUN chmod -R a+rX ${SKILLS_DIR}

WORKDIR /workspace