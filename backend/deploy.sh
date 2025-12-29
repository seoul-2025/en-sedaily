#!/bin/bash
# Deploy Script for SEOdaily-ENG Backend
# Builds and deploys Lambda functions

set -e

echo "🚀 Starting SEOdaily-ENG Backend Deployment..."
echo ""

# ============================================
# Step 1: Build Lambda Package
# ============================================
echo "📦 Building Lambda package..."

# Clean previous builds
rm -rf lambda-build lambda_package.zip
mkdir lambda-build

# Install dependencies for Linux (Lambda runtime)
echo "  → Installing dependencies for Linux (Python 3.11)..."
pip3 install -r requirements.txt -t lambda-build \
  --platform manylinux2014_x86_64 \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  --no-cache-dir \
  --quiet

# Copy source code
echo "  → Copying source code..."
cp -r clients handlers utils config.py TRANSLATION_PROMPT.md lambda-build/

# Create ZIP package
echo "  → Creating ZIP package..."
cd lambda-build
zip -r ../lambda_package.zip . -q
cd ..

# Cleanup build directory
rm -rf lambda-build

# Get package size
PACKAGE_SIZE=$(du -h lambda_package.zip | cut -f1)
echo "  ✓ Package created: lambda_package.zip ($PACKAGE_SIZE)"
echo ""

# ============================================
# Step 2: Upload to S3
# ============================================
echo "📤 Uploading to S3..."
aws s3 cp lambda_package.zip s3://seodaily-eng-lambda-packages-dev/ --quiet
echo "  ✓ Uploaded to s3://seodaily-eng-lambda-packages-dev/lambda_package.zip"
echo ""

# ============================================
# Step 3: Update Lambda Functions
# ============================================
echo "🔄 Updating Lambda functions..."

# Define Lambda functions to update
LAMBDA_FUNCTIONS=(
  "seodaily-eng-article-collector-dev"
  "seodaily-eng-search-dev"
  "seodaily-eng-article-dev"
  "seodaily-eng-article-slug-dev"
)

# Update each function
for FUNCTION_NAME in "${LAMBDA_FUNCTIONS[@]}"; do
  echo "  → Updating $FUNCTION_NAME..."

  aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --s3-bucket seodaily-eng-lambda-packages-dev \
    --s3-key lambda_package.zip \
    --region us-east-1 \
    --output json \
    --query 'LastModified' \
    > /dev/null

  echo "    ✓ Updated successfully"
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 Monitoring commands:"
echo "  → Article Collector logs:"
echo "     aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow"
echo "  → Search API logs:"
echo "     aws logs tail /aws/lambda/seodaily-eng-search-dev --follow"
echo "  → Article API logs:"
echo "     aws logs tail /aws/lambda/seodaily-eng-article-dev --follow"
echo ""