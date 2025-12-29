#!/bin/bash
set -e

echo "Building Lambda package..."

# Clean previous builds
rm -rf lambda-build lambda-package.zip
mkdir lambda-build

# Install dependencies with Linux platform
echo "Installing dependencies for Linux..."
pip3 install -r requirements.txt -t lambda-build \
  --platform manylinux2014_x86_64 \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  --no-cache-dir

# Copy code
echo "Copying code..."
cp -r clients handlers utils config.py TRANSLATION_PROMPT.md lambda-build/

# Create zip package
echo "Creating package..."
cd lambda-build
zip -r ../lambda-package.zip . -q
cd ..

echo "✅ Lambda package created: lambda-package.zip"

# Upload to S3
echo "Uploading to S3..."
aws s3 cp lambda-package.zip s3://seodaily-eng-frontend-dev-us-east-1/lambda/lambda-linux.zip

# Update Lambda functions
echo "Updating Lambda functions..."
aws lambda update-function-code \
  --region us-east-1 \
  --function-name seodaily-eng-search-dev \
  --s3-bucket seodaily-eng-frontend-dev-us-east-1 \
  --s3-key lambda/lambda-linux.zip

aws lambda update-function-code \
  --region us-east-1 \
  --function-name seodaily-eng-article-dev \
  --s3-bucket seodaily-eng-frontend-dev-us-east-1 \
  --s3-key lambda/lambda-linux.zip

echo "✅ Deployment complete!"

# Keep package for Terraform
cp lambda-package.zip lambda_package.zip

# Cleanup build directory only
rm -rf lambda-build
