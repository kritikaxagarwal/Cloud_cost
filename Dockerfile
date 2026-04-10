FROM python:3.10-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv lock
COPY . .
RUN pip install openenv-core fastapi uvicorn gradio matplotlib numpy pandas openai python-dotenv pydantic hatchling
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
