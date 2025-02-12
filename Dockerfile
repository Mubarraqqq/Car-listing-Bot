ARG CACHEBUST=1
# Use an official Python image
FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Add Google's official GPG key and repository for Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Debug: Print installed Google Chrome version
RUN google-chrome --version

# Download the correct ChromeDriver version
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1) && \
    DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION) && \
    echo "Installing ChromeDriver version: $DRIVER_VERSION" && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Debug: Print installed ChromeDriver version
RUN chromedriver --version

# Set environment variables so Selenium can find Chrome and ChromeDriver
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Set the working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the Flask port (Railway will supply the PORT environment variable)
EXPOSE 5000

# Debug command: Verify Chrome and ChromeDriver installation when the container starts
CMD ["bash", "-c", "google-chrome --version && chromedriver --version && python app.py"]