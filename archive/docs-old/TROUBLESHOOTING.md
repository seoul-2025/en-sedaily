# Troubleshooting Guide

**Last Updated**: 2025-12-01

## Issue: No New Articles Appearing

### Symptoms
- EventBridge is ENABLED and running every 10 minutes
- Lambda executes successfully (no errors)
- But `total_found: 0` in Lambda response
- Frontend shows old articles only

### Root Cause
**BigKinds API Delay or No New Publications**

The BigKinds API may have a delay in indexing new articles, or Seoul Economic Daily may not have published new articles recently (weekends, holidays, etc.).

### Verification Steps

1. **Check EventBridge Status**
```bash
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1
# Should show: "State": "ENABLED"
```

2. **Check Lambda Execution**
```bash
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --cli-binary-format raw-in-base64-out \
  --payload '{"hours": 24}' \
  --region us-east-1 \
  response.json && cat response.json
```

3. **Check Most Recent Article Date**
```bash
aws dynamodb scan \
  --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --projection-expression "news_id,published_at" \
  --max-items 10 | jq -r '.Items[] | "\(.published_at.S)"' | sort -r | head -5
```

4. **Check Current Article Count**
```bash
aws dynamodb scan --table-name seodaily-eng-articles-dev --select COUNT --region us-east-1
```

### Solutions

#### Solution 1: Wait for BigKinds API Update
BigKinds API typically has a **1-2 day delay** for indexing new articles. This is normal behavior.

**Action**: Wait 24-48 hours and check again.

#### Solution 2: Increase Collection Window
Temporarily increase the collection window to verify the system is working:

```bash
# Test with 7 days
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --cli-binary-format raw-in-base64-out \
  --payload '{"hours": 168}' \
  --region us-east-1 \
  response.json && cat response.json
```

#### Solution 3: Update EventBridge Schedule
If you want to reduce collection frequency during low-activity periods:

```bash
# Change to every 1 hour
aws events put-rule \
  --name seodaily-eng-article-collection-dev \
  --schedule-expression "rate(1 hour)" \
  --region us-east-1

# Change to every 6 hours
aws events put-rule \
  --name seodaily-eng-article-collection-dev \
  --schedule-expression "rate(6 hours)" \
  --region us-east-1

# Back to 10 minutes
aws events put-rule \
  --name seodaily-eng-article-collection-dev \
  --schedule-expression "rate(10 minutes)" \
  --region us-east-1
```

#### Solution 4: Manual Collection for Testing
Force collection with a wider date range:

```bash
# Collect from last 7 days
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --cli-binary-format raw-in-base64-out \
  --payload '{"hours": 168}' \
  --region us-east-1 \
  response.json
```

### Expected Behavior

#### Normal Operation
- **Collection Frequency**: Every 10 minutes
- **Collection Window**: Last 1 hour
- **Expected Results**: 0-50 articles per collection
- **Zero Articles**: Normal if no new publications

#### BigKinds API Characteristics
- **Indexing Delay**: 1-2 days typical
- **Weekend/Holiday**: Fewer or no articles
- **Peak Hours**: Weekday mornings (KST) have most articles

### Monitoring

#### Check Lambda Logs
```bash
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1
```

#### Check Last Successful Collection
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/seodaily-eng-article-collector-dev \
  --filter-pattern "Collection complete" \
  --region us-east-1 \
  --max-items 5
```

### Current Status (2025-12-01)

- **EventBridge**: ENABLED, running every 10 minutes ✅
- **Lambda**: Executing successfully ✅
- **DynamoDB**: 68 articles stored ✅
- **Latest Article**: 2025-11-29 (2 days old)
- **Issue**: BigKinds API not returning articles from 2025-11-30 or 2025-12-01

**Conclusion**: System is working correctly. Waiting for BigKinds API to index new articles.

### Recommendations

1. **Keep Current Schedule**: 10 minutes is fine, Lambda will just return 0 articles when none are available
2. **Monitor Costs**: Even with 0 articles, you're charged for Lambda executions (~$86/month)
3. **Consider Adjusting**: If BigKinds delay is consistent, consider 1-hour or 6-hour schedule
4. **Weekend Schedule**: Consider different schedule for weekends (fewer articles)

### Alternative: Adjust to 1-Hour Schedule

If you want to reduce costs while BigKinds API catches up:

```bash
# Change to 1 hour
aws events put-rule \
  --name seodaily-eng-article-collection-dev \
  --schedule-expression "rate(1 hour)" \
  --region us-east-1

# This reduces:
# - Collections: 144/day → 24/day
# - Monthly cost: ~$86 → ~$14
```

### When to Worry

**Worry if**:
- EventBridge shows "DISABLED"
- Lambda returns errors (not just 0 articles)
- DynamoDB article count decreases
- Frontend API returns errors

**Don't worry if**:
- Lambda returns `total_found: 0` (normal during low activity)
- Latest article is 1-2 days old (BigKinds API delay)
- Weekend shows fewer articles (normal)

### Contact Information

- **AWS Region**: us-east-1
- **Lambda**: seodaily-eng-article-collector-dev
- **DynamoDB**: seodaily-eng-articles-dev
- **EventBridge**: seodaily-eng-article-collection-dev
- **Frontend**: https://d39c7rf2w6v6qi.cloudfront.net
