# Use an existing Python image
FROM python:latest

# Set working directory inside the container
WORKDIR /app

# Copy all project files into /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start the app
CMD ["python", "main.py"]