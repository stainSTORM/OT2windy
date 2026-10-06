# Opentrons OT-2 as an Arkitekt app, for the openUC2 OS (os-rpi) and any Docker host.
#   docker build -t ot2windy .
#   docker run -p 8080:8080 -v ~/ot2:/config ot2windy   -> http://localhost:8080/
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev
COPY app.py arkitekt_bind.py config.example.yaml ./
COPY OT2Driver OT2Driver
# config.yaml, extra protocols (protocols/) and the stored login (.state/) live in /config.
ENV OT2_CONFIG=/config/config.yaml
RUN useradd -u 1000 -m app && mkdir /config && chown app /config
USER app
EXPOSE 8080
CMD ["python", "app.py"]
