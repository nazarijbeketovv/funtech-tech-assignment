FROM python:3.12.11-slim-bullseye

ARG UV_INDEX

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y apt-utils \
    gcc \
    make

COPY uv.lock pyproject.toml ./

RUN uv venv && uv sync

COPY Makefile alembic.ini ./
COPY ./src ./src
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "python3", "-m", "gunicorn", \
"-b", "0.0.0.0:8000", \
"--workers", "1", \
"--access-logfile", "-", \
"-k", "uvicorn.workers.UvicornWorker", \
"main:create_app()" ]
