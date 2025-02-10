#!/usr/bin/env bash

# Install Chrome
echo "Installing Chrome..."
wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > google-chrome.deb
sudo dpkg -i google-chrome.deb || sudo apt-get -f install -y

# Install ChromeDriver (must match Chrome version)
echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

echo "Chrome and ChromeDriver installed successfully!"
