# Use an official Python image
FROM python:3.12

# Install system dependencies
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

# Ensure ChromeDriver version matches Chromium
RUN CHROMIUM_VERSION=$(chromium --version | awk '{print $2}' | cut -d '.' -f1,2,3) \
    && LATEST_DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json" | jq -r --arg CHROME "$CHROMIUM_VERSION" '.builds[$CHROME]') \
    && wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${LATEST_DRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && mv /usr/bin/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /usr/bin/chromedriver-linux64

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]