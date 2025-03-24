# Use an official Python runtime as a base image
# sudo docker build -t arkitekt_opentrons .
FROM python:3.10-slim

# Set environment variables to prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ot2_driver.py .

# Expose any ports the app runs on
EXPOSE 8000
# additional port for Arkitekt?

# Run the script
CMD ["python", "ot2_driver.py"]

