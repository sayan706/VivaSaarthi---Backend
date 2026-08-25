# VivaSaarthi backend — single-stage build.
# Pure-Python app; every dependency ships manylinux wheels (psycopg2-binary,
# Pillow, gevent, ...), so there is no compile stage to cache — one slim stage
# keeps the image small and the build simple.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first so requirement changes don't invalidate the layer.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# TCP probe: any accepted connection means the WSGI server is up.
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD ["python", "-c", "import socket; s=socket.create_connection(('127.0.0.1', 5000), 3); s.close()"]

ENTRYPOINT ["./entrypoint.sh"]
