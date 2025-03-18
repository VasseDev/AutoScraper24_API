# Use an official Python image
FROM python:3.13-slim

# Install Poetry
RUN python -m pip install poetry

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the application
COPY . .

# Install the application
RUN poetry install --no-interaction --no-ansi

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the FastAPI server
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]