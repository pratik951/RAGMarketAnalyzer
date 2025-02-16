FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend and frontend directories
COPY backend /app/backend/
COPY frontend /app/frontend/

# Copy the .env file
COPY .env /app/.env

# Set the entry point for the application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
