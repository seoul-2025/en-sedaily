#!/bin/bash

# Create Global Secondary Index (GSI) for slug-based article lookups
#
# This script creates a GSI on the 'slug' attribute of the DynamoDB table.
# The GSI enables efficient querying of articles by their SEO-friendly slug.
#
# Prerequisites:
# - AWS CLI installed and configured
# - Proper IAM permissions for DynamoDB operations
#
# Usage:
#   ./create_gsi.sh
#
# Note: GSI creation is asynchronous and takes 10-30 minutes to complete.

set -e  # Exit on error

TABLE_NAME="seodaily-eng-articles-dev"
REGION="us-east-1"
INDEX_NAME="slug-index"

echo "=================================================="
echo "Creating Global Secondary Index for Slug Lookups"
echo "=================================================="
echo ""
echo "Table: $TABLE_NAME"
echo "Region: $REGION"
echo "Index: $INDEX_NAME"
echo ""

# Check if table exists
echo "1. Checking if table exists..."
if ! aws dynamodb describe-table \
  --table-name "$TABLE_NAME" \
  --region "$REGION" \
  --output json > /dev/null 2>&1; then
  echo "ERROR: Table '$TABLE_NAME' does not exist in region '$REGION'"
  exit 1
fi
echo "✓ Table exists"
echo ""

# Check if GSI already exists
echo "2. Checking if GSI already exists..."
EXISTING_GSI=$(aws dynamodb describe-table \
  --table-name "$TABLE_NAME" \
  --region "$REGION" \
  --output json \
  | jq -r ".Table.GlobalSecondaryIndexes[]? | select(.IndexName==\"$INDEX_NAME\") | .IndexName")

if [ "$EXISTING_GSI" == "$INDEX_NAME" ]; then
  echo "✓ GSI '$INDEX_NAME' already exists"
  echo ""
  echo "GSI Status:"
  aws dynamodb describe-table \
    --table-name "$TABLE_NAME" \
    --region "$REGION" \
    --output json \
    | jq ".Table.GlobalSecondaryIndexes[] | select(.IndexName==\"$INDEX_NAME\") | {IndexName, IndexStatus, Projection}"
  exit 0
fi
echo "✓ GSI does not exist yet"
echo ""

# Create GSI
echo "3. Creating GSI '$INDEX_NAME'..."
echo "   This will take 10-30 minutes to complete..."
echo ""

aws dynamodb update-table \
  --table-name "$TABLE_NAME" \
  --region "$REGION" \
  --attribute-definitions \
    AttributeName=slug,AttributeType=S \
  --global-secondary-index-updates \
    "[{
      \"Create\": {
        \"IndexName\": \"$INDEX_NAME\",
        \"KeySchema\": [{\"AttributeName\":\"slug\",\"KeyType\":\"HASH\"}],
        \"Projection\": {\"ProjectionType\":\"ALL\"},
        \"ProvisionedThroughput\": {
          \"ReadCapacityUnits\": 5,
          \"WriteCapacityUnits\": 5
        }
      }
    }]" \
  --output json > /dev/null

echo "✓ GSI creation initiated successfully"
echo ""

# Monitor GSI creation status
echo "4. Monitoring GSI creation status..."
echo "   Status will be checked every 30 seconds"
echo "   Press Ctrl+C to stop monitoring (GSI will continue creating)"
echo ""

while true; do
  STATUS=$(aws dynamodb describe-table \
    --table-name "$TABLE_NAME" \
    --region "$REGION" \
    --output json \
    | jq -r ".Table.GlobalSecondaryIndexes[]? | select(.IndexName==\"$INDEX_NAME\") | .IndexStatus")

  if [ "$STATUS" == "ACTIVE" ]; then
    echo ""
    echo "=================================================="
    echo "✓ GSI creation completed successfully!"
    echo "=================================================="
    echo ""
    echo "GSI Details:"
    aws dynamodb describe-table \
      --table-name "$TABLE_NAME" \
      --region "$REGION" \
      --output json \
      | jq ".Table.GlobalSecondaryIndexes[] | select(.IndexName==\"$INDEX_NAME\")"
    break
  elif [ "$STATUS" == "CREATING" ]; then
    echo "   Status: CREATING... (waiting)"
    sleep 30
  elif [ "$STATUS" == "" ]; then
    echo "ERROR: GSI not found"
    exit 1
  else
    echo "   Status: $STATUS"
    sleep 30
  fi
done

echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo ""
echo "1. Run migration script to populate slugs for existing articles:"
echo "   cd /path/to/backend"
echo "   python3 scripts/migrate_slugs.py --dry-run"
echo "   python3 scripts/migrate_slugs.py"
echo ""
echo "2. Deploy updated Lambda functions"
echo "3. Test slug-based article retrieval"
echo ""
