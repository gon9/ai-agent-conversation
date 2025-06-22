FROM python:3.11-slim

WORKDIR /app

# Install uv for package management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY .python-version .
COPY app/ app/

# Create virtual environment and install dependencies
RUN uv venv .venv
RUN uv pip install -e .

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
