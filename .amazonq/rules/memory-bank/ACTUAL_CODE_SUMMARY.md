# Actual Code Summary - 2025-01-08

**Last Updated**: 2025-01-08 (Verified by reading actual files)

## Backend Code (Python 3.11)

### Clients (6 files)

**bigkinds_client.py**:
- Article dataclass with 10 fields
- `search_news()`: fields parameter, default ["news_id", "published_at"]
- `get_article_detail()`: asyncio.sleep(1), batch 100, uses provider_link_page
- HTTPS conversion: `replace("http://", "https://", 1)`
- ValidationError for invalid inputs

**translation_service.py**:
- Model: claude-opus-4-5-20251101
- `_load_translation_prompt()`: Reads TRANSLATION_PROMPT.md from parent dir
- httpx.AsyncClient with 60.0 timeout
- API: https://api.anthropic.com/v1/messages
- Max tokens: 8192
- Returns: data["content"][0]["text"]

**dynamodb_client.py**:
- `batch_check_exists()`: batch_get_item, 100 item limit, returns set
- `save_article()`: put_item + get_item verification
- Saves 13 fields including SEO metadata

**response_validator.py**:
- `validate_and_sanitize_bigkinds_search()`: Returns sanitized dict
- `validate_and_sanitize_bigkinds_detail()`: Includes provider_link_page
- Raises ResponseValidationError

**cache_manager.py** (Unused):
- Redis with 2s timeout, 7 days TTL
- `generate_cache_key()`: "{article_id}:{field}:{lang}"

**validation.py**:
- validate_query, validate_date_format, validate_api_key
- All return bool

### Handlers (5 files)

**article_collector.py**:
- KST: `timezone(timedelta(hours=9))`
- Pagination: 100 per batch, max 10,000
- Fields: ["news_id", "published_at", "provider_link_page"]
- `batch_check_exists()` for deduplication
- Chunking: `[full_text[i:i+4000] for i in range(0, len(full_text), 4000)]`
- SEO extraction: regex for Meta Description, Keywords, Hashtags
- Category: `category[0].split('>')[0]`

**search_handler.py**:
- `table.scan()`: Full table scan
- Python filtering: content, query, date, category
- Sort: `items.sort(key=lambda x: x.get('published_at', ''), reverse=True)`
- Pagination: Python slicing

**article_handler.py**:
- DynamoDB-only: `await self.dynamodb_client.get_article(article_id)`
- Returns 13 fields including SEO metadata
- No BigKinds fallback

**cms_update_handler.py**:
- Direct `table.update_item()`
- 6 updatable fields + updated_at
- CORS headers

**cms_delete_handler.py**:
- Direct `table.delete_item()`
- CORS headers

**error_handler.py**:
- ErrorCode enum (10 types)
- ErrorResponse dataclass
- `_sanitize_log_message()`: Regex redaction

## Frontend Code (Next.js 14 + TypeScript)

### App Pages

**page.tsx** (Homepage):
- `'use client'`
- `fetchLatestArticles(7, 15)`
- transformArticle function
- Featured: articles[0], Top: [1-5], Popular: [6-10]
- JSON-LD: WebSite with SearchAction

**[category]/page.tsx**:
- CATEGORY_CONFIG with 7 categories
- generateStaticParams()

**[category]/CategoryClient.tsx**:
- `fetchCategoryArticles(category, 1, 20)`
- Load More button
- lg:grid-cols-12 (8 main + 4 sidebar)
- Most Read: articles.slice(1, 6)

**article/page.tsx**:
- Suspense wrapper
- `useSearchParams()` for ID
- Hashtags: `split(/[,\s]+/)`
- Related: 3 articles
- JSON-LD: NewsArticle

**search/page.tsx**:
- `highlightText()`: Regex with <mark>
- Pagination: maxVisible=7
- Result boxes: `bg-[rgb(50,50,50)]`

### Components

**Header.tsx**:
- Search: `absolute left-8 top-6`
- Logo: `absolute right-8 top-6`, w-24 h-16
- 7 categories with hover effects

**utils/api.ts**:
- 5 functions: fetchLatestArticles, fetchCategoryArticles, fetchRelatedArticles, searchArticles, fetchArticleDetail
- CATEGORY_MAP: 7 categories → Korean names

**globals.css**:
- Font: 'Noto Sans', 'Malgun Gothic'
- --color-brand-blue: #1E40AF
- --color-text: #222222
- --color-bg: #FFFFFF

**next.config.js**:
- output: 'export'
- swcMinify: true
- compiler.removeConsole: production only

## CMS Code (Next.js 14)

**page.tsx** (Main):
- Auth check: localStorage.getItem('cms_auth')
- Redirects to /login if not authenticated
- News ID input form
- Logout button

**login/page.tsx**:
- Password: sedaily2024!
- localStorage.setItem('cms_auth', 'true')

**edit/page.tsx**:
- Auth check on mount
- 6 editable fields
- Save: POST /api/update-article
- Delete: POST /api/delete-article

## Infrastructure Code (Terraform)

**main.tf**:
- Lambda: 1024MB, Python 3.11
- CloudFront OAC for S3
- API Gateway with CORS

**eventbridge.tf**:
- rate(1 hour)
- article_collector Lambda

**dynamodb_articles.tf**:
- GSI: category-published_at-index
- PAY_PER_REQUEST billing

## Key Patterns

**Backend**:
- Async/await everywhere
- Dataclasses for models
- Static methods for validation
- Regex for sanitization
- Pydantic Settings

**Frontend**:
- 'use client' for interactivity
- useState/useEffect
- Suspense wrappers
- CSS variables
- Tailwind utilities

**Infrastructure**:
- Terraform declarative
- Lambda proxy integration
- CloudFront OAC
- Static export

## Actual Metrics

- First Load JS: 97.1kB
- Lambda Memory: 1024MB
- Initial Load: 15 articles
- API Response: 2.5s (uncached)
- Total Articles: 1,475+
- Cost: $71/month
