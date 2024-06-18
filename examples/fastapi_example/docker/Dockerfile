FROM public.ecr.aws/docker/library/python:3.11.9-slim-bookworm as builder

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    gcc \
    python3-dev
RUN pip install --upgrade pip && pip install poetry==1.8.1

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root && \
    poetry cache clear --all .

COPY . /app

FROM public.ecr.aws/docker/library/python:3.11.9-slim-bookworm as runner

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app
