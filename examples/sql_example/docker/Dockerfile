FROM public.ecr.aws/docker/library/python:3.13.12-slim-bookworm AS builder

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    ca-certificates

ADD https://astral.sh/uv/0.10.9/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/opt/.venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY compose/ ./compose/
COPY examples/sql_example/pyproject.toml ./examples/sql_example/

RUN uv sync --frozen --no-dev --package sql-example && \
    uv cache clean

COPY examples/sql_example/ ./examples/sql_example/

FROM public.ecr.aws/docker/library/python:3.13.12-slim-bookworm AS runner

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/examples/sql_example

COPY --from=builder /opt/.venv /opt/.venv
COPY --from=builder /app/examples/sql_example /app/examples/sql_example
COPY --from=builder /app/compose /app/compose

ENV PATH="/opt/.venv/bin:$PATH"
