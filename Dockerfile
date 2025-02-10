# Use an official Python image
FROM python:3.12

# Install Chrome & ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
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
RUN CHROME_VERSION=$(chromium --version | grep -o '[0-9]*\.[0-9]*\.[0-9]*') \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && rm /tmp/chromedriver.zip

# Set execution permissions
RUN chmod +x /usr/bin/chromedriver

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
