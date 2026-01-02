## Database Schema

### DynamoDB Tables

**seodaily-eng-articles-dev**
```python
{
  "news_id": str,              # Partition Key (e.g., "02100311.20251223092834001")
  "slug": str,                 # SEO-friendly URL slug (e.g., "samsung-q4-earnings")
  "title": str,                # Original Korean title
  "title_en": str,             # English translated title
  "content": str,              # Original Korean content
  "content_en": str,           # English translated content
  "category": str,             # Korean category (경제, IT_과학, 정치, 사회, 문화, 스포츠, 국제)
  "published_at": str,         # ISO format with actual time (2025-12-23T09:28:34.000+09:00)
  "byline": str,               # English reporter name (e.g., "By Tae-gyu Lee")
  "original_link": str,        # Seoul Economic article URL (HTTPS)
  "meta_description": str,     # SEO meta description (150-160 chars)
  "keywords": List[str],       # SEO keywords (5-8 keywords)
  "hashtags": List[str],       # Article hashtags (e.g., ["#Samsung", "#SemiconductorExports"])
  "created_at": str,           # ISO format
  "updated_at": str            # ISO format
}
```

**seodaily-eng-metadata-dev**
```python
{
  "metadata_key": str,         # Partition Key (e.g., "collection_stats")
  "total_articles": int,       # Total articles collected
  "last_collection_time": str, # ISO format
  "articles_per_category": {
    "finance": int,
    "technology": int,
    # ...
  },
  "translation_errors": int,
  "success_rate": float        # Percentage
}
```

### Indexes

- **Primary Key**: news_id (Partition Key)
- **GSI1**: slug-index (for SEO-friendly URL lookups)
- **GSI2**: category-published_date-index (for category filtering)
- **GSI3**: published_date-index (for chronological sorting)

---

