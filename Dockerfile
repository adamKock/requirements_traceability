# Use an existing Python image
FROM python:latest

# Set working directory inside the container
WORKDIR /app

# Copy all project files into /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir fastapi pydantic uvicorn pandas sentence-transformers torch python-multipart

# Expose port
EXPOSE 8000

# Start the app
CMD ["python", "main.py"]