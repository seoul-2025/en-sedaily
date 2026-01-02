# Article Collection Policy

**Date**: 2025-12-04
**Status**: ✅ ACTIVE

## Collection Rules

### ✅ ACCEPT: Articles with content
- Must have `content` field with non-empty text
- Will be translated and saved to DynamoDB

### ❌ REJECT: Articles without content
- If `content` is empty or whitespace only
- Will NOT be saved to DynamoDB

### ⚠️ OPTIONAL: original_link
- Preferred: `provider_link_page` from BigKinds API
- If missing: Article is still saved (link will be None/null)
- No fallback links generated

## Implementation

### Content Validation (REQUIRED)
```python
# Skip articles without content
if not article.content or not article.content.strip():
    logger.info(f"Skipping article {article.news_id} - no content")
    continue  # Do NOT save
```

### Link Handling (OPTIONAL)
```python
# Log if no link, but still save article
if not article.original_link:
    logger.warning(f"Article {article.news_id} has no provider_link_page")

# Save to DynamoDB (original_link can be None)
saved = await dynamodb_client.save_article({
    'news_id': article.news_id,
    'original_link': article.original_link,  # Can be None
    ...
})
```

## Link Source

### Only `provider_link_page`
```python
# ONLY use provider_link_page
original_link = doc.get("provider_link_page")

# Convert http to https
if original_link and original_link.startswith("http://"):
    original_link = original_link.replace("http://", "https://", 1)
```

### No Fallbacks
- ❌ No `news_url` fallback
- ❌ No constructed links
- ✅ If BigKinds doesn't provide `provider_link_page`, it stays None

## Results

### Articles WITH links
- Display with clickable link to Seoul Economic
- Better user experience

### Articles WITHOUT links
- Still displayed on website
- No clickable link (or could show "Link unavailable")
- Content is still valuable

## Benefits

### ✅ Maximum Content Coverage
- All articles with content are saved
- No articles lost due to missing links

### ✅ Simple Logic
- Only one rejection criteria: no content
- Easy to understand and maintain

### ✅ Link Quality
- When links exist, they are proper `provider_link_page` format
- No mixed link formats

## Frontend Handling

### Display Logic
```typescript
// Article detail page
{article.original_link ? (
  <a href={article.original_link} target="_blank">
    Read Original Article
  </a>
) : (
  <span className="text-gray-500">
    Original link unavailable
  </span>
)}
```

## Monitoring

### Check articles without links
```bash
aws dynamodb scan --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --filter-expression "attribute_not_exists(original_link) OR original_link = :null" \
  --expression-attribute-values '{":null":{"NULL":true}}' \
  --select COUNT
```

### Check articles without content (should be 0)
```bash
aws dynamodb scan --table-name seodaily-eng-articles-dev \
  --region us-east-1 \
  --filter-expression "attribute_not_exists(content_en) OR content_en = :empty" \
  --expression-attribute-values '{":empty":{"S":""}}' \
  --select COUNT
```

## Summary

**ONLY reject**: No content
**Accept with warning**: No link
**Link source**: Only `provider_link_page` (no fallbacks)

✅ Deployed: 2025-12-04
