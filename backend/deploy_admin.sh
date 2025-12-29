#!/bin/bash
# Deploy Admin Lambda Functions

set -e

echo "🚀 Deploying Admin Lambda Functions..."

# Check if lambda_package.zip exists
if [ ! -f "lambda_package.zip" ]; then
    echo "❌ lambda_package.zip not found. Run build_lambda.sh first."
    exit 1
fi

# Add admin_handler.py to existing package
echo "📦 Adding admin_handler.py to lambda package..."
zip -g lambda_package.zip handlers/admin_handler.py

# Upload to S3
echo "☁️  Uploading to S3..."
aws s3 cp lambda_package.zip s3://seodaily-eng-lambda-packages-dev/lambda-admin.zip

echo "✅ Package uploaded successfully!"
echo ""
echo "Next steps:"
echo "1. Run: cd ../infrastructure"
echo "2. Run: terraform apply"
echo "3. This will create 5 new Lambda functions for CMS"
