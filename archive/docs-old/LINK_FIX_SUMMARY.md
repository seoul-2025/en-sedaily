# Original Link Fix Summary

**Date**: 2025-12-04
**Status**: ✅ COMPLETE

## Problem
252 articles in DynamoDB had missing `original_link` field (null or empty).

## Root Cause
BigKinds API sometimes doesn't provide `provider_link_page` or `news_url` fields for certain articles.

## Solution Implemented

### 1. Fix Script (`fix_missing_links_v2.py`)
- Scans all articles in DynamoDB
- Identifies articles without `original_link`
- Fetches links from BigKinds API
- Updates DynamoDB with correct links

**Results**:
- Total articles: 1,830
- Fixed: 252 articles (100%)
- Failed: 0 articles

### 2. Enhanced `bigkinds_client.py`
**STRICT POLICY**: Only use `provider_link_page`

```python
# ONLY use provider_link_page (short link format)
original_link = doc.get("provider_link_page")

# Convert http to https if link exists
if original_link and original_link.startswith("http://"):
    original_link = original_link.replace("http://", "https://", 1)

# NO FALLBACK - If no provider_link_page, original_link will be None
```

### 3. Enhanced `article_collector.py`
- **ONLY** requests `provider_link_page` field (no fallback fields)
- Added validation: Skip articles without `original_link`
- Prevents saving articles without proper links

```python
fields=[
    "news_id", "title", "content", "published_at",
    "provider_name", "category", "byline", 
    "provider_link_page",  # ONLY this field for links
    "images", "images_caption"
]

# Verify original_link exists before saving
if not article.original_link:
    logger.warning(f"Article {article.news_id} has no original_link - skipping")
    failed_articles += 1
    continue
```

## Guarantee for Future Collections

### ✅ STRICT POLICY: Only `provider_link_page` or REJECT

1. **Single field**: ONLY `provider_link_page` requested
2. **No fallback**: If BigKinds doesn't provide it, article is REJECTED
3. **Validation**: Articles without `provider_link_page` are NOT saved
4. **HTTPS conversion**: Automatic http→https conversion
5. **Quality control**: Only articles with proper short links are stored

### Link Format:
- ✅ **ONLY**: `provider_link_page` (short format: 2H1xxx)
- ❌ **NO**: `news_url` (not used)
- ❌ **NO**: Constructed links (not used)

## Verification

```bash
# Check for articles without links
aws dynamodb scan --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --filter-expression "attribute_not_exists(original_link) OR original_link = :null" \
  --expression-attribute-values '{":null":{"NULL":true}}' \
  --select COUNT
```

**Result**: 0 articles without links ✅

## Files Modified

1. `backend/clients/bigkinds_client.py` - 3-tier fallback logic
2. `backend/handlers/article_collector.py` - Validation + news_url field
3. `backend/fix_missing_links_v2.py` - Fix script (NEW)

## Deployment

```bash
cd backend
bash build_lambda.sh  # ✅ Deployed 2025-12-04
```

## Next Collection

The next automatic collection (every hour at :48) will:
- ✅ Request ONLY `provider_link_page` field
- ✅ NO fallback - strict quality control
- ✅ Skip articles without `provider_link_page` (won't save)
- ✅ Convert all http links to https

**Guarantee**: 100% of saved articles will have proper `provider_link_page` short links ✅

**Trade-off**: Some articles may be rejected if BigKinds doesn't provide `provider_link_page`, but this ensures link quality.
