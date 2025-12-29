# Strict Link Policy - Provider Link Page Only

**Date**: 2025-12-04
**Status**: ✅ ENFORCED

## Policy

### ✅ ACCEPT: Articles with `provider_link_page`
- Short link format: `https://www.sedaily.com/NewsView/2H1LKHKPJ1`
- Clean, user-friendly URLs
- Provided by BigKinds API

### ❌ REJECT: Articles without `provider_link_page`
- No fallback to `news_url`
- No constructed links from `news_id`
- Article will NOT be saved to DynamoDB

## Implementation

### 1. `bigkinds_client.py`
```python
# ONLY use provider_link_page
original_link = doc.get("provider_link_page")

# Convert http to https
if original_link and original_link.startswith("http://"):
    original_link = original_link.replace("http://", "https://", 1)

# If no provider_link_page, original_link = None
```

### 2. `article_collector.py`
```python
# Request ONLY provider_link_page
fields=[
    "news_id", "title", "content", "published_at",
    "provider_name", "category", "byline", 
    "provider_link_page",  # ONLY this field
    "images", "images_caption"
]

# Reject articles without link
if not article.original_link:
    logger.warning(f"Article {article.news_id} has no provider_link_page - REJECTED")
    failed_articles += 1
    continue  # Skip saving
```

## Benefits

### ✅ Quality Control
- All saved articles have proper short links
- Consistent link format across all articles
- No fallback URLs that might break

### ✅ User Experience
- Clean, short URLs for sharing
- Direct links to Seoul Economic articles
- Professional appearance

### ✅ Maintainability
- Simple, single-source link logic
- No complex fallback chains
- Easy to debug and verify

## Trade-offs

### ⚠️ Potential Article Loss
- Some articles may not have `provider_link_page` in BigKinds API
- These articles will be rejected and not saved
- Estimated impact: <5% of articles (based on current data)

### ✅ Acceptable Trade-off
- Quality over quantity
- Better to have fewer articles with proper links
- Than many articles with inconsistent or broken links

## Verification

### Check Current Database
```bash
# All articles should have provider_link_page format links
aws dynamodb scan --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --query 'Items[*].original_link.S' \
  --output text | grep -v "2H1" | wc -l
```

**Expected**: 0 (all links should have 2H1xxx format)

### Monitor Collection Logs
```bash
# Check for rejected articles
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev \
  --follow --region us-east-1 | grep "no provider_link_page"
```

## Current Status

- ✅ All 1,830 articles have `provider_link_page` links
- ✅ Lambda deployed with strict policy (2025-12-04)
- ✅ Next collection will enforce this policy
- ✅ No fallback logic in place

## Future Collections

Every hour at :48, the collector will:
1. Fetch articles from BigKinds API
2. Request `provider_link_page` field
3. Check if `provider_link_page` exists
4. If YES → Translate and save
5. If NO → Log warning and skip (reject)

**Result**: 100% of saved articles will have proper short links ✅
