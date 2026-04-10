FROM python:3.10-slim
WORKDIR /app
RUN pip install uv hatchling
COPY pyproject.toml .
RUN uv lock && cp uv.lock /tmp/uv.lock
COPY . .
RUN cp /tmp/uv.lock . && uv sync --no-dev || pip install openenv-core fastapi uvicorn gradio matplotlib numpy pandas openai python-dotenv pydantic
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
