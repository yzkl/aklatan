## ---------------- Builder stage ---------------- ##
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /uvx /bin/

# Copy project dependencies
WORKDIR /app
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
RUN uv sync --locked

## ---------------- Production stage ------------ ##
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY ./src ./src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
