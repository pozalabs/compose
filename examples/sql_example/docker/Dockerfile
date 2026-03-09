FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm AS builder

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends gcc python3-dev
RUN pip install --upgrade pip && pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY compose/ ./compose/
COPY examples/sql_example/pyproject.toml ./examples/sql_example/

RUN uv sync --frozen --no-dev --package sql-example

COPY examples/sql_example/ ./examples/sql_example/

FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm AS runner

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/examples/sql_example

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/examples/sql_example /app/examples/sql_example
COPY --from=builder /app/compose /app/compose

ENV PATH="/app/.venv/bin:$PATH"
