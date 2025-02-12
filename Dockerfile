# Use official Python image
FROM python:3.12

# Install system dependencies (including Chrome)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    jq \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install chromedriver-autoinstaller (fixes your issue)
RUN pip install chromedriver-autoinstaller

# Copy the application code
COPY . .

# Automatically download the correct ChromeDriver version at runtime
RUN python -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"

# Expose Flask port (for Railway)
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]