# Use an official Python image
FROM python:3.12

# Install Microsoft Edge & EdgeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    software-properties-common && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /usr/share/keyrings/microsoft.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" | tee /etc/apt/sources.list.d/microsoft-edge.list && \
    apt-get update && apt-get install -y \
    microsoft-edge-stable && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for Edge
ENV EDGE_BIN=/usr/bin/microsoft-edge-stable
ENV PATH="/usr/local/bin:$PATH"

# Install Edge WebDriver (Matching Edge Version)
RUN EDGE_VERSION=$(microsoft-edge-stable --version | awk '{print $3}') \
    && echo "Detected Edge version: $EDGE_VERSION" \
    && DRIVER_URL="https://msedgedriver.azureedge.net/$EDGE_VERSION/edgedriver_linux64.zip" \
    && wget -O /tmp/edgedriver.zip "$DRIVER_URL" \
    && unzip /tmp/edgedriver.zip -d /usr/local/bin/ \
    && rm /tmp/edgedriver.zip

# Ensure EdgeDriver is executable
RUN chmod +x /usr/local/bin/msedgedriver \
    && ln -s /usr/local/bin/msedgedriver /usr/bin/msedgedriver

# Set the working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Edge WebDriver Manager dependency
RUN pip install webdriver-manager gunicorn

# **Copy only the templates folder first**  
COPY templates/ templates/

# Copy the rest of the app code
COPY . .

# Ensure Flask runs on port 5000
ENV FLASK_RUN_PORT=5000
EXPOSE 5000

# Run Flask app with Gunicorn on port 5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]