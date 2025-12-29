# Lambda Environment Variables Update - 2025-01-XX

## Issue Discovered

**Problem**: Lambda 함수들이 Anthropic API 키 환경 변수 없이 배포되어 있었음
- 코드는 Anthropic Claude 사용하도록 작성됨
- 하지만 Lambda 환경 변수에 `ANTHROPIC_API_KEY`가 없었음
- 결과: 번역이 실패하거나 fallback 로직 사용 가능성

## Root Cause

Lambda 함수 배포 시 환경 변수가 업데이트되지 않음:
- `build_lambda.sh`는 코드만 업데이트
- 환경 변수는 별도로 설정 필요

## Solution Applied

### 1. Environment Variables Added

모든 Lambda 함수에 다음 환경 변수 추가:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
BIGKINDS_API_KEY=your_bigkinds_api_key_here
BIGKINDS_API_URL=https://tools.kinds.or.kr
DYNAMODB_TABLE_ARTICLES=seodaily-eng-articles-dev
REGION=us-east-1
LOG_LEVEL=INFO
```

### 2. Updated Lambda Functions

✅ **seodaily-eng-article-collector-dev**
- Status: Updated
- Date: 2025-01-XX
- Environment Variables: 7 keys

✅ **seodaily-eng-search-dev**
- Status: Updated
- Date: 2025-01-XX
- Environment Variables: 7 keys

✅ **seodaily-eng-article-dev**
- Status: Updated
- Date: 2025-01-XX
- Environment Variables: 7 keys

### 3. Verification Commands

```bash
# Check environment variables
aws lambda get-function-configuration \
  --function-name seodaily-eng-article-collector-dev \
  --region us-east-1 \
  --query 'Environment.Variables' \
  --output json

# Verify all functions
for func in seodaily-eng-article-collector-dev seodaily-eng-search-dev seodaily-eng-article-dev; do
  echo "=== $func ==="
  aws lambda get-function-configuration \
    --function-name $func \
    --region us-east-1 \
    --query 'Environment.Variables' \
    --output json | jq 'keys'
done
```

## Impact

### Before Update
- ❌ Lambda 환경 변수에 `ANTHROPIC_API_KEY` 없음
- ❌ 번역 실패 가능성
- ❌ Fallback 로직 사용 (AWS Translate 또는 에러)

### After Update
- ✅ 모든 Lambda 함수에 Anthropic API 키 설정
- ✅ Claude Opus 4.5 모델 ID 설정
- ✅ 정상적인 번역 작동 보장

## Testing

### Manual Test
```bash
# Trigger collector manually
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json

# Check logs for Anthropic API calls
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev \
  --since 5m \
  --region us-east-1 | grep -i "anthropic\|claude"
```

### Expected Log Output
```
[INFO] Translating article 02100311.20251204140144001
[INFO] Anthropic API call successful
[INFO] HTTP Request: POST https://api.anthropic.com/v1/messages "HTTP/1.1 200 OK"
```

## Future Prevention

### Deployment Checklist
1. ✅ Update code (`build_lambda.sh`)
2. ✅ Update environment variables (AWS CLI or Console)
3. ✅ Verify environment variables
4. ✅ Test with manual invocation
5. ✅ Check CloudWatch logs

### Automated Solution
Create deployment script that updates both code and environment variables:

```bash
#!/bin/bash
# deploy_lambda_full.sh

# Build and upload code
./build_lambda.sh

# Update environment variables
for func in seodaily-eng-article-collector-dev seodaily-eng-search-dev seodaily-eng-article-dev; do
  aws lambda update-function-configuration \
    --function-name $func \
    --region us-east-1 \
    --environment "Variables={
      ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY,
      ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101,
      BIGKINDS_API_KEY=$BIGKINDS_API_KEY,
      BIGKINDS_API_URL=https://tools.kinds.or.kr,
      DYNAMODB_TABLE_ARTICLES=seodaily-eng-articles-dev,
      REGION=us-east-1,
      LOG_LEVEL=INFO
    }"
done
```

## Status

✅ **Complete** - All Lambda functions now have correct environment variables for Anthropic Claude API

**Updated**: 2025-01-XX
**By**: Amazon Q Developer
**Verified**: Environment variables confirmed in all 3 Lambda functions
