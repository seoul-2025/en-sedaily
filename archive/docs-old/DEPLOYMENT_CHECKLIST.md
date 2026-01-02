# Deployment Checklist

**Last Updated**: 2025-12-01 14:30 KST

## Quick Reference

### Frontend Deployment (UI/Code Changes Only)
```bash
cd frontend
rm -rf .next out  # CRITICAL
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```

### Backend Deployment
```bash
cd backend
./build_lambda.sh
```

### Infrastructure Deployment
```bash
cd infrastructure
terraform apply
```

## When to Deploy What

### Frontend Rebuild Required ✅
- UI/design changes
- Component code changes
- Configuration changes (next.config.js)
- Style changes (CSS, Tailwind)

### Frontend Rebuild NOT Required ❌
- New articles added (automatic via EventBridge)
- Article updates (handled by DynamoDB)
- Content changes (client-side loading)

### Backend Deployment Required ✅
- Lambda function code changes
- API endpoint changes
- Search/article logic changes
- Translation logic changes

### Infrastructure Deployment Required ✅
- EventBridge schedule changes
- DynamoDB table changes
- IAM permission changes
- New AWS resources

## Pre-Deployment Checklist

### Frontend
- [ ] Test locally (`npm run dev`)
- [ ] Build successfully (`npm run build`)
- [ ] Check build output (15 pages expected)
- [ ] Verify no errors in console
- [ ] Test all routes work

### Backend
- [ ] Test Lambda functions locally
- [ ] Run pytest (`pytest -v`)
- [ ] Check environment variables
- [ ] Verify API Gateway endpoints
- [ ] Test with real BigKinds API

### Infrastructure
- [ ] Review Terraform plan (`terraform plan`)
- [ ] Check for resource deletions
- [ ] Verify IAM permissions
- [ ] Confirm EventBridge schedule

## Post-Deployment Verification

### Frontend
- [ ] Visit live URL: https://d39c7rf2w6v6qi.cloudfront.net
- [ ] Test homepage loads
- [ ] Test article detail page
- [ ] Test category pages (all 7)
- [ ] Test search functionality
- [ ] Hard refresh browser (Cmd+Shift+R)
- [ ] Check CloudFront invalidation status

### Backend
- [ ] Check Lambda logs in CloudWatch
- [ ] Test API endpoints manually
- [ ] Verify search returns results
- [ ] Verify article detail works
- [ ] Check EventBridge is enabled

### Real-time Updates
- [ ] Verify EventBridge rule is ENABLED
- [ ] Check last collection time in logs
- [ ] Wait 10 minutes and verify new collection
- [ ] Refresh frontend and see new articles

## Rollback Procedures

### Frontend Rollback
```bash
# Re-deploy previous version
cd frontend
git checkout <previous-commit>
rm -rf .next out
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```

### Backend Rollback
```bash
# Re-deploy previous Lambda version
aws lambda update-function-code \
  --function-name seodaily-eng-search-dev \
  --s3-bucket seodaily-eng-lambda-packages-dev \
  --s3-key lambda_package_<previous-version>.zip
```

### Infrastructure Rollback
```bash
cd infrastructure
git checkout <previous-commit>
terraform apply
```

## Common Issues

### Issue: Frontend changes not visible
**Solution**: 
1. Clear CloudFront cache
2. Hard refresh browser (Cmd+Shift+R)
3. Wait 1-2 minutes for invalidation

### Issue: New articles not appearing
**Solution**:
1. Check EventBridge is enabled
2. Check Lambda logs for errors
3. Manually trigger collection
4. Refresh frontend page

### Issue: Build fails
**Solution**:
1. Delete `.next` and `out` folders
2. Run `npm install` again
3. Check for TypeScript errors
4. Verify environment variables

### Issue: Lambda deployment fails
**Solution**:
1. Check Docker is running
2. Verify AWS credentials
3. Check S3 bucket exists
4. Review IAM permissions

## Monitoring Commands

### Check EventBridge Status
```bash
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1
```

### View Lambda Logs
```bash
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1
```

### Check DynamoDB Count
```bash
aws dynamodb scan --table-name seodaily-eng-articles-dev --select COUNT --region us-east-1
```

### Manual Collection Trigger
```bash
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json
```

## Emergency Contacts

- **AWS Region**: us-east-1
- **CloudFront Distribution**: EUWQ1K71CXJUH
- **S3 Bucket**: seodaily-eng-frontend-dev-us-east-1
- **DynamoDB Tables**: seodaily-eng-articles-dev, seodaily-eng-metadata-dev
- **EventBridge Rule**: seodaily-eng-article-collection-dev

## Notes

- Frontend rebuild takes ~15 seconds
- CloudFront invalidation takes 1-2 minutes
- Lambda deployment takes ~30 seconds
- EventBridge runs every 10 minutes
- Articles accumulate continuously (never deleted)
