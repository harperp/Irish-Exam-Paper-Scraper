#!/bin/bash
# Setup script to download ChromeDriver locally (no sudo required)

set -e

echo "=== ChromeDriver Local Setup for macOS ==="
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

# Create drivers directory in project
DRIVER_DIR="./drivers"
mkdir -p "$DRIVER_DIR"

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

# Move to project directory
cd - > /dev/null
mv "$TMP_DIR/$CHROMEDRIVER_BIN" "$DRIVER_DIR/chromedriver"

# Remove quarantine attribute (macOS security)
echo "Removing macOS quarantine attribute..."
xattr -d com.apple.quarantine "$DRIVER_DIR/chromedriver" 2>/dev/null || true

# Cleanup
rm -rf "$TMP_DIR"

echo
echo "✓ ChromeDriver installed successfully to: $DRIVER_DIR/chromedriver"
echo
echo "Verifying installation..."
"$DRIVER_DIR/chromedriver" --version

echo
echo "=== Setup Complete ==="
echo
echo "Note: The exam_scraper.py script has been configured to use this local driver."
