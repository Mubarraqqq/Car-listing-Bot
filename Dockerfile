# Use an official Python image
FROM python:3.12

# Install system dependencies including Chromium and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    jq \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables so your app knows where Chrome and ChromeDriver are located
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set the working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the Flask port (Railway will pass the PORT variable)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]