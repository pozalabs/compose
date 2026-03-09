FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm AS builder

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends gcc python3-dev
RUN pip install --upgrade pip && pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY compose/ ./compose/
COPY examples/fastapi_example/pyproject.toml ./examples/fastapi_example/

RUN uv sync --frozen --no-dev --package fastapi-example

COPY examples/fastapi_example/ ./examples/fastapi_example/

FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm AS runner

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/examples/fastapi_example

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/examples/fastapi_example /app/examples/fastapi_example
COPY --from=builder /app/compose /app/compose

ENV PATH="/app/.venv/bin:$PATH"
