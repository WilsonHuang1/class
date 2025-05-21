FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default environment variables
ENV PORT=5001
ENV S3_BUCKET_NAME=hw06-zhh20013-1

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]