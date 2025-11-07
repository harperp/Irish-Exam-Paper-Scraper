#!/bin/bash
# Setup script to download and install ChromeDriver on macOS

set -e

echo "=== ChromeDriver Setup for macOS ==="
echo

# Check if Chrome is installed
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo "❌ Google Chrome is not installed."
    echo "Please install Chrome from: https://www.google.com/chrome/"
    exit 1
fi

# Get Chrome version
CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version | awk '{print $3}' | cut -d '.' -f 1)
echo "✓ Found Google Chrome version: $CHROME_VERSION"

# Determine the appropriate ChromeDriver version
echo "Fetching latest compatible ChromeDriver version..."

# For Chrome 115+, use the new JSON endpoint
if [ "$CHROME_VERSION" -ge 115 ]; then
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}")
    DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/mac-x64/chromedriver-mac-x64.zip"
else
    # For older Chrome versions
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
    DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_mac64.zip"
fi

echo "ChromeDriver version: $CHROMEDRIVER_VERSION"
echo

# Create temp directory
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

echo "Downloading ChromeDriver..."
curl -L -o chromedriver.zip "$DOWNLOAD_URL"

echo "Extracting..."
unzip -q chromedriver.zip

# Find the chromedriver binary (location varies by version)
if [ -f "chromedriver-mac-x64/chromedriver" ]; then
    CHROMEDRIVER_BIN="chromedriver-mac-x64/chromedriver"
elif [ -f "chromedriver" ]; then
    CHROMEDRIVER_BIN="chromedriver"
else
    echo "❌ Could not find chromedriver binary in downloaded archive"
    exit 1
fi

# Make it executable
chmod +x "$CHROMEDRIVER_BIN"

# Install to /usr/local/bin
INSTALL_DIR="/usr/local/bin"
echo
echo "Installing ChromeDriver to $INSTALL_DIR..."
echo "(This may require your password)"

sudo mkdir -p "$INSTALL_DIR"
sudo mv "$CHROMEDRIVER_BIN" "$INSTALL_DIR/chromedriver"

# Remove quarantine attribute (macOS security)
echo "Removing macOS quarantine attribute..."
sudo xattr -d com.apple.quarantine "$INSTALL_DIR/chromedriver" 2>/dev/null || true

# Cleanup
cd - > /dev/null
rm -rf "$TMP_DIR"

echo
echo "✓ ChromeDriver installed successfully!"
echo
echo "Verifying installation..."
chromedriver --version

echo
echo "=== Setup Complete ==="
