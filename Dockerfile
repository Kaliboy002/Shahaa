# Use a base image with Python
FROM python:3.12-slim

# Install system dependencies (including libGL)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the application code
COPY . /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "blur_background.py"]
