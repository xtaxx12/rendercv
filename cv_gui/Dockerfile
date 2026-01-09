FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copiar archivos
COPY requirements.txt .
COPY app.py .
COPY templates/ templates/

# Copiar ejemplos para previews
COPY ../examples/ /app/examples/

# Instalar dependencias Python
RUN uv pip install --system -r requirements.txt
RUN uv pip install --system "rendercv[full]"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
