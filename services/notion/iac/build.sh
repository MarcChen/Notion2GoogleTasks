#!/bin/bash

# Build script for Lambda function deployment package
set -e

echo "Building Lambda deployment package..."

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Using temporary directory: $TEMP_DIR"

# Create a virtual environment in temp directory
echo "Creating virtual environment..."
python3 -m venv "$TEMP_DIR/venv"
source "$TEMP_DIR/venv/bin/activate"

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies in virtual environment
echo "Installing Python dependencies..."
pip install -r requirements.txt --no-cache-dir

# Create deployment directory
DEPLOY_DIR="$TEMP_DIR/deploy"
mkdir -p "$DEPLOY_DIR"

# Copy Lambda function code
cp webhook_handler.py "$DEPLOY_DIR/webhook_handler.py"

# Copy installed packages (excluding venv directories)
echo "Copying dependencies..."
cp -r "$TEMP_DIR/venv/lib/python"*/site-packages/* "$DEPLOY_DIR/"

# Remove unnecessary files to reduce package size
echo "Cleaning up unnecessary files..."
find "$DEPLOY_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$DEPLOY_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$DEPLOY_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find "$DEPLOY_DIR" -name "*.pyc" -delete 2>/dev/null || true

# Create deployment package
echo "Creating deployment package..."
cd "$DEPLOY_DIR"
zip -r webhook_handler.zip . -x "*.pyc" "*__pycache__*"

# Move the package back to the original directory
mv webhook_handler.zip "$OLDPWD/"

# Deactivate virtual environment
deactivate

echo "Deployment package created: webhook_handler.zip"

# Cleanup
rm -rf "$TEMP_DIR"

echo "Build completed successfully!"

echo "Deployment package created: webhook_handler.zip"

# Cleanup
rm -rf "$TEMP_DIR"

echo "Build completed successfully!"
