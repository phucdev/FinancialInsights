FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# uv for dependency mgmt
RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# install only API extras
RUN uv venv && . .venv/bin/activate && uv sync --frozen

COPY services/api/app /app/app
EXPOSE 8000
CMD ["/bin/bash","-lc",". .venv/bin/activate && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
