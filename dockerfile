# Use an official Python runtime as a base image
# Build: sudo docker build -t arkitekt_opentrons .
# Clean Cache https://stackoverflow.com/questions/62473932/at-least-one-invalid-signature-was-encountered
# Run: sudo docker run -it --rm --name arkitekt_opentrons arkitekt_opentrons
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install debian-archive-keyring first, then update and install build-essential
RUN apt-get update && \
    apt-get install -y debian-archive-keyring && \
    apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
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

