# Deployment Log - 2025-12-04

## Issue: Original Link Not Populated

### Problem
- New articles collected by `article_collector` Lambda were not getting `original_link` (provider_link_page) populated in DynamoDB
- Manual update scripts worked fine, but automatic collection failed

### Root Cause
**BigKinds API only returns fields explicitly requested in the `fields` parameter**

According to `bigkinds-ultimate-guide.md` Section 3.6:
- The `fields` parameter in search API determines which fields are returned
- If `provider_link_page` is not in the `fields` array, it won't be returned
- The search API was only requesting `["news_id", "published_at"]`

### Solution

#### 1. Updated `bigkinds_client.py`
- Added `fields` parameter to `search_news()` method signature
- Made fields configurable with default minimal fields
- Applied fields parameter to API payload

```python
async def search_news(
    self,
    query: str,
    published_from: str,
    published_until: str,
    providers: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    return_from: int = 0,
    return_size: int = 10,
    fields: Optional[List[str]] = None  # NEW
) -> SearchResult:
```

#### 2. Updated `article_collector.py`
- Modified search API call to include `provider_link_page` in fields
- Now requests: `["news_id", "published_at", "provider_link_page"]`

```python
search_result = await bigkinds_client.search_news(
    query="",
    published_from=from_date.strftime("%Y-%m-%d"),
    published_until=until.strftime("%Y-%m-%d"),
    providers=["서울경제"],
    return_from=return_from,
    return_size=batch_size,
    fields=["news_id", "published_at", "provider_link_page"]  # NEW
)
```

### Deployment

**Date**: 2025-12-04 13:28 KST
**Method**: `./build_lambda.sh`

**Updated Lambda Functions**:
1. `seodaily-eng-search-dev` - Updated
2. `seodaily-eng-article-dev` - Updated  
3. `seodaily-eng-article-collector-dev` - Updated

**Package Size**: 34.2 MB
**Status**: ✅ All functions deployed successfully

### Expected Result
- New articles collected will now have `original_link` populated from search API
- Short link format: `https://www.sedaily.com/NewsView/2H1xxx`
- HTTPS conversion applied automatically

### Verification Steps
1. Wait for next hourly collection (at :48)
2. Check CloudWatch logs for `article_collector`
3. Verify new articles in DynamoDB have `original_link` field
4. Confirm links are in short format (2H1xxx)

### Documentation Updated
- ✅ `BACKEND_ARCHITECTURE.md` - Added fields parameter documentation
- ✅ `DEPLOYMENT_LOG_2025-12-04.md` - This file

### Key Learnings
1. **Always check API documentation for field requirements**
2. **BigKinds API requires explicit field specification**
3. **Search API can return provider_link_page if requested**
4. **No need to rely solely on detail API for links**

### Related Files
- `backend/clients/bigkinds_client.py` - Modified
- `backend/handlers/article_collector.py` - Modified
- `bigkinds-ultimate-guide.md` - Reference documentation
