# Real-time Article Update System

**Last Updated**: 2025-12-01 16:00 KST

## Overview

Automated system to collect, translate, and publish new Seoul Economic articles **every 1 hour** with real-time frontend updates.

## Architecture

```
EventBridge Scheduler (every 1 hour)
  ↓
Lambda: article_collector (본문 있는 기사만 수집)
  ↓
BigKinds API (서울경제 전용)
  ↓
AWS Translate (한글 → 영어)
  ↓
DynamoDB (seodaily-eng-articles-dev) - 계속 누적
  ↓
Frontend (클라이언트 사이드 로딩 - 새로고침 시 최신 기사)
```

## Current Status

### ✅ Live and Running
- **Schedule**: Every 1 hour
- **Region**: us-east-1
- **Collection Window**: Last 1 hour
- **Frontend**: Client-side data loading (no rebuild needed)
- **Cost**: ~$14/month (24 collections/day)
- **Previous**: 10 minutes ($86/month) → **84% cost reduction**

### EventBridge Rule
```bash
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1
# Schedule: rate(1 hour)
# State: ENABLED
```

## Key Features

### 1. Content Filtering
- ✅ Articles without content are **automatically skipped**
- ✅ Only articles with `content` field are translated and stored
- ✅ Double filtering: Collection stage + Search stage

### 2. Automatic Updates
- ✅ New articles added to DynamoDB every 1 hour
- ✅ Frontend fetches latest data on page load
- ✅ **No frontend rebuild required**
- ✅ User refresh = Latest articles displayed

### 3. Article Accumulation
- ✅ Articles **never deleted** from DynamoDB
- ✅ Continuous accumulation (68 → 73 → 78 → ...)
- ✅ Deduplication by `news_id`
- ✅ Unlimited storage capacity

### 4. Dynamic Article Count
- ✅ Variable article count per collection (0-50)
- ✅ Depends on Seoul Economic publishing schedule
- ✅ System handles any quantity automatically

## Frontend Real-time Updates

### How It Works
```javascript
// Client-side data loading
useEffect(() => {
  fetchLatestArticles() // API call on page load
}, []);
```

### Article Display Logic
- **Featured**: Most recent article (articles[0])
- **Top Stories**: 2nd-6th most recent (articles[1-5])
- **Most Popular**: 7th-11th most recent (articles[6-10])
- **Sections**: Category-filtered latest articles

### Update Flow
1. EventBridge triggers collection (every 1 hour)
2. New articles saved to DynamoDB
3. User refreshes page
4. API returns latest sorted articles
5. **Featured article automatically changes** to newest

## Components

### 1. Article Collector Lambda
- **File**: `backend/handlers/article_collector.py`
- **Function**: `seodaily-eng-article-collector-dev`
- **Timeout**: 5 minutes (300s)
- **Memory**: 512 MB
- **Trigger**: EventBridge (every 1 hour)

### 2. Search Handler Lambda
- **File**: `backend/handlers/search_handler.py`
- **Function**: `seodaily-eng-search-dev`
- **Features**: 
  - Title + Content search
  - Case-insensitive
  - Date filtering
  - Category filtering
  - Content existence check

### 3. DynamoDB Table
- **Table**: `seodaily-eng-articles-dev`
- **Primary Key**: `news_id`
- **Attributes**: title_ko, title_en, content_ko, content_en, published_at, category, provider
- **Storage**: Unlimited, pay-per-request

### 4. Frontend (Client-Side)
- **Homepage**: `src/app/page.tsx` (client component)
- **Category Pages**: `src/app/[category]/CategoryClient.tsx`
- **Data Loading**: useEffect + API calls
- **No Rebuild**: Static HTML + Dynamic data

## Deployment

### Backend Deployment
```bash
cd backend
./build_lambda.sh
# Automatically builds and deploys Lambda functions
```

### Frontend Deployment
```bash
cd frontend
rm -rf .next out
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```

**Note**: Frontend rebuild only needed for UI/code changes, NOT for new articles.

## Monitoring

### Check EventBridge Status
```bash
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1
```

### View Collection Logs
```bash
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1
```

### Check Last Collection
```bash
aws logs filter-log-events \
  --log-group-name /aws/lambda/seodaily-eng-article-collector-dev \
  --filter-pattern "Collection complete" \
  --region us-east-1 \
  --max-items 1
```

### Manual Trigger
```bash
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json && cat response.json
```

## Cost Estimation

### Current (1-hour intervals)
- **Collections per day**: 24
- **Collections per month**: 720
- **Total per month**: ~$14

### Breakdown
- AWS Translate: ~$11/month
- Lambda: ~$2/month
- DynamoDB: ~$1/month
- S3/CloudFront: ~$5/month

### Previous (10-minute intervals)
- Collections: 144/day, 4,320/month
- Cost: ~$86/month
- **Savings**: $72/month (84% reduction)

## Configuration

### Change Schedule Frequency
```bash
# Edit schedule (requires AWS CLI)
aws events put-rule \
  --name seodaily-eng-article-collection-dev \
  --schedule-expression "rate(10 minutes)" \
  --region us-east-1
```

Options:
- `rate(5 minutes)` - Every 5 minutes
- `rate(10 minutes)` - Every 10 minutes
- `rate(30 minutes)` - Every 30 minutes
- `rate(1 hour)` - Every 1 hour (current)
- `rate(6 hours)` - Every 6 hours

### Change Collection Window
```bash
# Edit EventBridge target input
aws events put-targets \
  --rule seodaily-eng-article-collection-dev \
  --targets '[{"Id":"1","Arn":"arn:aws:lambda:us-east-1:887078546492:function:seodaily-eng-article-collector-dev","Input":"{\"hours\":1}"}]' \
  --region us-east-1
```

## Troubleshooting

### No New Articles Appearing
1. Check EventBridge is enabled
2. Check Lambda logs for errors
3. Verify BigKinds API is returning results
4. Check DynamoDB for new entries

### Frontend Not Updating
1. **Refresh the page** (F5 or Cmd+R)
2. Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
3. Check browser console for API errors
4. Verify API Gateway is responding

### EventBridge Not Triggering
```bash
# Check rule status
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1

# Enable if disabled
aws events enable-rule --name seodaily-eng-article-collection-dev --region us-east-1
```

## Important Notes

### ✅ What Happens Automatically
- New articles collected every 1 hour
- Articles translated and stored in DynamoDB
- Frontend displays latest articles on refresh
- Featured article changes to newest
- All pages update with new content
- Articles accumulate continuously (never deleted)

### ❌ What Doesn't Happen
- Frontend does NOT auto-refresh (user must refresh)
- Old articles are NOT deleted
- Articles without content are NOT stored
- Frontend does NOT need rebuild for new articles

### 🔄 User Experience
1. User visits site → Sees latest articles
2. 1 hour passes → New articles collected
3. User refreshes → Sees new articles immediately
4. Featured article updates to newest
5. No manual intervention needed

### 📅 Seoul Economic Publishing Schedule
- **Weekdays**: Active publishing (multiple articles per day)
- **Weekends**: No publishing (Saturday, Sunday)
- **Holidays**: No publishing
- **BigKinds API Delay**: 1-2 days typical

## Live URLs

- **Frontend**: https://eng.sedaily.ai
- **CloudFront**: https://d39c7rf2w6v6qi.cloudfront.net
- **API Gateway**: https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev

## Support Commands

### Disable Auto-Collection
```bash
aws events disable-rule --name seodaily-eng-article-collection-dev --region us-east-1
```

### Enable Auto-Collection
```bash
aws events enable-rule --name seodaily-eng-article-collection-dev --region us-east-1
```

### Check DynamoDB Article Count
```bash
aws dynamodb scan --table-name seodaily-eng-articles-dev --select COUNT --region us-east-1
```
