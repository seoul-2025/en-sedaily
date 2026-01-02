# API Gateway Route Configuration

## Current Status

✅ **Lambda function deployed**: `seodaily-eng-article-slug-handler-dev`
❌ **API Gateway route**: Not yet configured

## Required Configuration

### Add New Route to API Gateway

**API Gateway ID**: `7w5nco7xn4` (from existing URL)
**Region**: `us-east-1`

### Step-by-Step Instructions

#### Option 1: AWS Console (Recommended)

1. **Open API Gateway Console**
   - Go to: https://console.aws.amazon.com/apigateway/
   - Select region: `us-east-1`
   - Find API: `seodaily-eng-api-dev` (or similar name with ID `7w5nco7xn4`)

2. **Create Resource**
   - Click "Resources" in left sidebar
   - Navigate to `/api/article` resource
   - Click "Actions" → "Create Resource"
   - Resource Name: `by-slug`
   - Resource Path: `by-slug`
   - Click "Create Resource"

3. **Create Child Resource for Slug Parameter**
   - Select the newly created `/api/article/by-slug` resource
   - Click "Actions" → "Create Resource"
   - Resource Name: `slug`
   - Resource Path: `{slug}` (with curly braces)
   - Click "Create Resource"

4. **Create GET Method**
   - Select `/api/article/by-slug/{slug}` resource
   - Click "Actions" → "Create Method"
   - Select "GET" from dropdown
   - Click checkmark

5. **Configure Method Integration**
   - Integration type: `Lambda Function`
   - Lambda Region: `us-east-1`
   - Lambda Function: `seodaily-eng-article-slug-handler-dev`
   - Click "Save"
   - Click "OK" to grant permissions

6. **Enable CORS**
   - Select `/api/article/by-slug/{slug}` resource
   - Click "Actions" → "Enable CORS"
   - Keep default settings
   - Click "Enable CORS and replace existing CORS headers"

7. **Deploy API**
   - Click "Actions" → "Deploy API"
   - Deployment stage: `dev`
   - Click "Deploy"

8. **Test the Endpoint**
   ```bash
   curl -s 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/article/by-slug/cambodias-top-university-delegation-visits-busan-to-launch' | python3 -m json.tool | head -30
   ```

   Expected response:
   ```json
   {
     "news_id": "02100311.20251222103805001",
     "title": "Cambodia's top university delegation visits Busan to launch...",
     "content": "...",
     "slug": "cambodias-top-university-delegation-visits-busan-to-launch",
     ...
   }
   ```

#### Option 2: AWS CLI

```bash
# 1. Get API ID
API_ID="7w5nco7xn4"
REGION="us-east-1"

# 2. Get root resource ID
ROOT_ID=$(aws apigatewayv2 get-apis --region $REGION --query "Items[?ApiId=='${API_ID}'].ApiId" --output text)

# 3. Get /api/article resource ID
ARTICLE_RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --region $REGION \
  --query "items[?path=='/api/article'].id" \
  --output text)

# 4. Create /api/article/by-slug resource
BY_SLUG_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --region $REGION \
  --parent-id $ARTICLE_RESOURCE_ID \
  --path-part "by-slug")

BY_SLUG_ID=$(echo $BY_SLUG_RESOURCE | jq -r '.id')

# 5. Create /api/article/by-slug/{slug} resource
SLUG_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --region $REGION \
  --parent-id $BY_SLUG_ID \
  --path-part "{slug}")

SLUG_ID=$(echo $SLUG_RESOURCE | jq -r '.id')

# 6. Create GET method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --region $REGION \
  --resource-id $SLUG_ID \
  --http-method GET \
  --authorization-type NONE

# 7. Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function \
  --function-name seodaily-eng-article-slug-handler-dev \
  --region $REGION \
  --query 'Configuration.FunctionArn' \
  --output text)

# 8. Configure Lambda integration
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --region $REGION \
  --resource-id $SLUG_ID \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations"

# 9. Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name seodaily-eng-article-slug-handler-dev \
  --region $REGION \
  --statement-id apigateway-invoke-slug-handler \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:$(aws sts get-caller-identity --query Account --output text):${API_ID}/*/*"

# 10. Deploy to dev stage
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --region $REGION \
  --stage-name dev
```

## Verification

After configuration, test both endpoints:

### 1. Test existing endpoint (should return slug field)
```bash
curl -s 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/article/02100311.20251222103805001' \
  | python3 -m json.tool | grep -A 1 '"slug"'
```

Expected output:
```
    "slug": "cambodias-top-university-delegation-visits-busan-to-launch",
```

### 2. Test new slug-based endpoint
```bash
curl -s 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/article/by-slug/cambodias-top-university-delegation-visits-busan-to-launch' \
  | python3 -m json.tool | head -30
```

Expected: Full article JSON response

## Troubleshooting

### Error: "Missing Authentication Token"
- Route not yet created in API Gateway
- Follow steps above to create route

### Error: "Internal server error"
- Check Lambda function logs:
  ```bash
  aws logs tail /aws/lambda/seodaily-eng-article-slug-handler-dev --follow --region us-east-1
  ```

### Error: "Article not found"
- Verify the slug exists in DynamoDB:
  ```bash
  aws dynamodb query \
    --table-name seodaily-eng-articles-dev \
    --index-name slug-index \
    --key-condition-expression "slug = :slug" \
    --expression-attribute-values '{":slug":{"S":"cambodias-top-university-delegation-visits-busan-to-launch"}}' \
    --region us-east-1
  ```

## Next Steps

After API Gateway route is configured:
1. ✅ Test backend slug endpoint
2. ✅ Test frontend with deployed backend
3. ⏳ Build and deploy frontend to EC2
4. ⏳ Verify production deployment
