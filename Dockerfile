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

# Set the working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Edge WebDriver Manager dependency
RUN pip install webdriver-manager

# Copy the app code
COPY . .

# Expose the Flask port (if needed)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]