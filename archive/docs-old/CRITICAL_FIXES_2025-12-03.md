# Critical Bug Fixes - 2025-12-03

## Summary
Fixed 6 critical bugs that were causing silent failures in article collection and storage.

## Bugs Fixed

### 1. Lambda Logging Not Working
**File**: `backend/handlers/article_collector.py`
**Problem**: `logging.basicConfig()` doesn't work in Lambda
**Fix**: Changed to `logger.setLevel(logging.INFO)`
**Impact**: All logs now visible in CloudWatch

### 2. DynamoDB Category Type Error
**File**: `backend/handlers/article_collector.py` (lines 145-157)
**Problem**: Category saved as List, GSI expects String
**Error**: `ValidationException: Type mismatch for Index Key category Expected: S Actual: L`
**Fix**: 
```python
# Always convert to string
if isinstance(category, list):
    category = category[0] if category else 'news'
category = str(category) if category else 'news'
```
**Impact**: 100% save success (was ~44% failure)

### 3. DynamoDB Save Not Verified
**File**: `backend/clients/dynamodb_client.py`
**Problem**: `put_item()` returned True but items not saved
**Fix**: Added verification read after save
```python
response = self.table.put_item(Item=item)
verify = self.table.get_item(Key={'news_id': news_id})
if 'Item' not in verify:
    return False
```
**Impact**: Actual failures now detected

### 4. Save Return Value Not Checked
**File**: `backend/handlers/article_collector.py` (lines 175-182)
**Problem**: `save_article()` failure ignored, `new_articles` still incremented
**Fix**: Check return value and increment `failed_articles` on failure
**Impact**: Accurate success/failure counts

### 5. BigKinds API Result Not Validated
**File**: `backend/clients/bigkinds_client.py`
**Problem**: Not checking `result == 0` in API response
**Fix**: Added validation
```python
if data.get("result") != 0:
    raise ValidationError(f"BigKinds API error: {error_msg}")
```
**Impact**: API errors properly caught

### 6. No Rate Limiting
**File**: `backend/clients/bigkinds_client.py`
**Problem**: No delay between API calls
**Fix**: Added 1 second delay before detail fetch
```python
await asyncio.sleep(1)
```
**Impact**: Respects API rate limits

## Test Results

### Before Fixes (04:42 execution)
- Logged: 5 articles "successfully saved"
- DynamoDB: 0 articles actually saved
- Errors: Silent failures, no error logs

### After Fixes (04:57 execution)
- Logged: 5 articles failed with clear error messages
- Root cause identified: Category type mismatch
- Fixed and retested

### Final Test (05:00 execution)
- Result: 12 articles saved, 0 failed
- DynamoDB: All 12 confirmed present
- Success rate: 100%

## Deployment

**Last Deployed**: 2025-12-03 14:09 KST
**Lambda Functions Updated**:
- seodaily-eng-article-collector-dev
- seodaily-eng-search-dev
- seodaily-eng-article-dev

**Next Auto Collection**: Every hour at :48

## Verification Commands

```bash
# Check logs
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --since 10m --region us-east-1

# Check DynamoDB count
aws dynamodb describe-table --table-name seodaily-eng-articles-dev --region us-east-1 | grep ItemCount

# Manual test
aws lambda invoke --function-name seodaily-eng-article-collector-dev --cli-binary-format raw-in-base64-out --payload '{"hours": 1}' --region us-east-1 /tmp/test.json && cat /tmp/test.json | jq '.body'
```

## Key Learnings

1. **Always verify writes**: Don't trust return values, verify actual data
2. **Lambda logging**: Use `logger.setLevel()` not `basicConfig()`
3. **Type consistency**: DynamoDB GSI requires exact type match
4. **API validation**: Always check result codes, not just HTTP status
5. **Rate limiting**: Respect API limits with delays
6. **Error visibility**: Log everything, silent failures are dangerous

## Files Modified

1. `backend/handlers/article_collector.py` - Logging, category handling, save verification
2. `backend/clients/dynamodb_client.py` - Save verification, error logging
3. `backend/clients/bigkinds_client.py` - API validation, rate limiting
4. `.amazonq/rules/memory-bank/recent-changes.md` - Documentation
5. `.amazonq/rules/memory-bank/new-project-direction.md` - Status update
6. `README.md` - Status update
