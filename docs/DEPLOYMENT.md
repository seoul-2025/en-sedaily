## Deployment

### Backend Deployment (Lambda Functions)

```bash
# Build Lambda package (Docker-based for Linux compatibility)
cd backend
./build_lambda.sh

# Deploy article collector
aws lambda update-function-code \
  --function-name seodaily-eng-article-collector-dev \
  --zip-file fileb://lambda_package.zip \
  --region us-east-1

# Deploy search handler
aws lambda update-function-code \
  --function-name seodaily-eng-search-dev \
  --zip-file fileb://lambda_package.zip \
  --region us-east-1

# Deploy article handler
aws lambda update-function-code \
  --function-name seodaily-eng-article-dev \
  --zip-file fileb://lambda_package.zip \
  --region us-east-1

# Update environment variables
aws lambda update-function-configuration \
  --function-name seodaily-eng-article-collector-dev \
  --environment Variables={ANTHROPIC_API_KEY=sk-ant-xxx} \
  --region us-east-1

# Verify deployment
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{}' \
  --region us-east-1 \
  response.json
```

### Frontend Deployment (EC2 SSR)

**Recommended Method: Automated Deployment Script**

```bash
# Navigate to frontend directory
cd /Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/frontend

# Run deployment script
./deploy.sh
```

**What deploy.sh does:**
1. ✅ Builds Next.js production bundle (standalone mode)
2. ✅ Automatically includes `.env.local` in deployment package
3. ✅ Creates tar archive with all necessary files
4. ✅ Backs up current version on server
5. ✅ Uploads and extracts new version
6. ✅ Restarts PM2 with updated environment variables
7. ✅ Validates deployment success

**Configuration:**
- Server: `52.21.195.0`
- User: `ubuntu`
- PEM Key: `../sedaily-eng-key.pem`
- PM2 App: `sedaily-eng`
- Port: `3000`

**After Deployment:**
```bash
# Invalidate CloudFront cache to serve new version
aws cloudfront create-invalidation \
  --distribution-id EUWQ1K71CXJUH \
  --paths "/*"

# Monitor deployment
ssh -i ../sedaily-eng-key.pem ubuntu@52.21.195.0 'pm2 logs sedaily-eng'
```

**Manual Deployment (Alternative)**

```bash
# SSH to EC2 instance
ssh -i ../sedaily-eng-key.pem ubuntu@52.21.195.0

# Navigate to app directory
cd ~/en-sedaily

# Build standalone Next.js app
npm run build

# Restart PM2
pm2 restart sedaily-eng

# Check status
pm2 status
pm2 logs sedaily-eng --lines 50
```

### Frontend Deployment (Legacy: S3+CloudFront)

**Note**: This method is deprecated. Use EC2 SSR instead.

```bash
cd frontend

# CRITICAL: Clean cache before build
rm -rf .next out

# Build static export
npm run build

# Upload to S3
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id EUWQ1K71CXJUH \
  --paths "/*"

# Verify deployment
curl https://en.sedaily.com
```

### Infrastructure Deployment

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply infrastructure changes
terraform apply

# Specific resource updates
terraform apply -target=aws_lambda_function.article_collector
terraform apply -target=aws_dynamodb_table.articles
```

---

