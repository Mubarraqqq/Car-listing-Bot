# Use an official Python image
FROM python:3.12

# Install system dependencies (Chromium, ChromeDriver, utilities)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    jq \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set Chrome and ChromeDriver paths
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . .

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]