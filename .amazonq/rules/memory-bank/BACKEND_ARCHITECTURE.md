# Backend Architecture

## Overview

Python 3.11 serverless backend using AWS Lambda, DynamoDB, and Anthropic Claude Opus 4.5 for automated Korean-to-English news translation.

**Last Updated**: 2025-01-XX (Phase 14: Anthropic Claude Integration)

## System Flow

```
EventBridge (hourly at :48)
  ↓
article_collector Lambda
  ↓
BigKinds API (Seoul Economic only)
  ↓
DynamoDB batch check (100 items)
  ↓
AWS Translate (4,000 char chunks)
  ↓
DynamoDB save + verify
  ↓
API Gateway (search/article endpoints)
  ↓
Frontend (client-side fetch)
```

## Lambda Functions

### 1. article_collector
**File**: `handlers/article_collector.py`  
**Trigger**: EventBridge every hour  
**Timeout**: 300s  
**Memory**: 512MB

**Process**:
1. Calculate today's date range (KST timezone, 00:00-23:59)
2. Search BigKinds API (provider: 서울경제, batch: 100, **fields: news_id, published_at, provider_link_page**)
3. Batch check existing articles (91% call reduction)
4. Fetch details for new articles only (100 per batch, 1s delay)
5. Translate in 4,000 char chunks
6. Save to DynamoDB with verification
7. Convert category List→String

**Key Features**:
- KST timezone: `timezone(timedelta(hours=9))`
- Batch duplicate check: `batch_check_exists()`
- Chunked translation: `content[i:i+4000]`
- HTTPS conversion: `http://` → `https://`
- Content filtering: Skip empty articles

### 2. search_handler
**File**: `handlers/search_handler.py`  
**Trigger**: API Gateway POST /api/search  
**Timeout**: 30s  
**Memory**: 512MB

**Process**:
1. Scan DynamoDB table
2. Filter by query (title + content, case-insensitive)
3. Filter by date range (Python-based)
4. Filter by category
5. Exclude articles without content
6. Sort by published_at DESC
7. Paginate results

**Key Features**:
- DynamoDB only (no BigKinds)
- Title + content search
- Case-insensitive matching
- Content existence check

### 3. article_handler
**File**: `handlers/article_handler.py`  
**Trigger**: API Gateway GET /api/article/{id}  
**Timeout**: 30s  
**Memory**: 512MB

**Process**:
1. Get article from DynamoDB by news_id
2. Return if found
3. Error if not found (no BigKinds fallback)

**Key Features**:
- DynamoDB only
- No caching (Redis unused)
- Simple retrieval

## Clients

### bigkinds_client.py
**Purpose**: BigKinds API integration

**Methods**:
- `search_news()`: Search articles (provider, date range, pagination, **fields**)
- `get_article_detail()`: Fetch full content (batch: 100, delay: 1s)

**Features**:
- Validates date format (YYYY-MM-DD)
- **Fields parameter support**: Request specific fields in search API
- Uses `provider_link_page` for short links
- Auto HTTPS conversion
- Rate limiting (1s delay)
- Response validation

**Critical**: BigKinds API only returns fields specified in `fields` parameter

### dynamodb_client.py
**Purpose**: DynamoDB operations

**Methods**:
- `save_article()`: Save + verify (read-after-write)
- `get_article()`: Retrieve by news_id
- `batch_check_exists()`: Check 100 items at once
- `article_exists()`: Single item check

**Features**:
- Batch operations (91% call reduction)
- Save verification
- Error logging

### translation_service.py
**Purpose**: AWS Translate integration

**Methods**:
- `translate()`: Single text translation
- `translate_batch()`: Multiple texts (sequential)

**Features**:
- Korean (ko) → English (en)
- Error handling
- Validation

### response_validator.py
**Purpose**: API response validation

**Methods**:
- `validate_bigkinds_search_response()`: Check structure
- `validate_bigkinds_detail_response()`: Check structure
- `validate_and_sanitize_bigkinds_detail()`: Clean + validate

**Features**:
- Structure validation
- Required field checks
- Sanitization with defaults
- Includes `provider_link_page`

### cache_manager.py
**Purpose**: Redis caching (currently unused)

**Methods**:
- `get()`: Retrieve from cache
- `set()`: Store with TTL
- `invalidate()`: Delete key

**Status**: Implemented but not used in production

### validation.py
**Purpose**: Input validation utilities

**Functions**:
- `validate_query()`: Non-empty check
- `validate_date_format()`: YYYY-MM-DD check
- `validate_api_key()`: Non-empty check
- `validate_translation_text()`: Non-empty check

## Error Handling

### error_handler.py
**Purpose**: Centralized error handling

**Features**:
- User-friendly messages
- Sensitive data sanitization
- Error code enum
- Specific handlers for BigKinds, Translation, Network errors

**Error Codes**:
- `BIGKINDS_API_ERROR`
- `TRANSLATION_ERROR`
- `NETWORK_ERROR`
- `VALIDATION_ERROR`
- `INTERNAL_ERROR`

## Data Models

### Article (BigKinds)
```python
@dataclass
class Article:
    news_id: str
    title: str
    content: Optional[str]
    published_at: str
    provider: str
    category: str
    byline: Optional[str]
    original_link: Optional[str]
    images: List[str]
    images_caption: List[str]
```

### DynamoDB Schema
```python
{
    'news_id': str,           # Primary key
    'title_ko': str,
    'title_en': str,
    'content_ko': str,
    'content_en': str,
    'published_at': str,
    'category': str,          # String (not List)
    'provider': str,
    'byline': Optional[str],
    'original_link': str,     # provider_link_page (HTTPS)
    'images': List[str],
    'images_caption': List[str],
    'translated_at': str      # ISO timestamp
}
```

## Configuration

### Environment Variables
```bash
BIGKINDS_API_KEY=254bec69-1c13-470f-904a-c4bc9e46cc80
BIGKINDS_API_URL=https://tools.kinds.or.kr
AWS_REGION=us-east-1
REGION=us-east-1
DYNAMODB_TABLE_ARTICLES=seodaily-eng-articles-dev
LOG_LEVEL=INFO
```

### BigKinds API
- **Provider**: 서울경제 only
- **Fields**: news_id, title, content, published_at, provider_name, category, byline, provider_link_page, images, images_caption
- **Rate Limit**: 1 second delay between calls
- **Batch Size**: 100 articles per request

### AWS Services
- **Translate**: Korean (ko) → English (en)
- **DynamoDB**: PAY_PER_REQUEST mode
- **Lambda**: Python 3.11 runtime
- **EventBridge**: `rate(1 hour)` schedule

## Performance Optimizations

### Batch Operations
- **Before**: 364 DynamoDB calls
- **After**: 4 DynamoDB calls
- **Reduction**: 91%

### Chunked Translation
- **Chunk Size**: 4,000 characters
- **Reason**: AWS Translate limit (10,000 bytes)
- **Process**: Split → Translate → Join

### Deduplication
- Batch check existing articles
- Skip translation if exists
- Update original_link only
- **Cost Savings**: 96% translation reduction

### Content Filtering
- Skip articles without content at collection
- Filter empty content in search
- **Result**: Only quality articles stored

## Deployment

### Build Process
```bash
./build_lambda.sh
```

**Steps**:
1. Install dependencies for Linux (manylinux2014_x86_64)
2. Copy code (clients, handlers, config.py)
3. Create zip package
4. Upload to S3
5. Update Lambda functions

### Lambda Package Structure
```
lambda-package.zip
├── clients/
│   ├── bigkinds_client.py
│   ├── dynamodb_client.py
│   ├── translation_service.py
│   ├── response_validator.py
│   ├── cache_manager.py
│   └── validation.py
├── handlers/
│   ├── article_collector.py
│   ├── search_handler.py
│   ├── article_handler.py
│   └── error_handler.py
├── config.py
└── [dependencies]
```

## Monitoring

### CloudWatch Logs
- `/aws/lambda/seodaily-eng-article-collector-dev`
- `/aws/lambda/seodaily-eng-search-dev`
- `/aws/lambda/seodaily-eng-article-dev`

### Key Metrics
- Collection success rate: 100%
- Translation success rate: ~99%
- DynamoDB save success: 100%
- API response time: <1s

### Manual Trigger
```bash
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json
```

## Cost Analysis

### Monthly Costs (~$289)
- **AWS Translate**: ~$270 (actual: $9.64/day)
- **Lambda**: ~$11 (720 invocations/month)
- **DynamoDB**: ~$3 (on-demand reads/writes)
- **S3**: ~$5 (storage + transfer)

### Optimization Impact
- **Batch checking**: 91% DynamoDB call reduction
- **Deduplication**: 96% translation cost savings
- **Hourly schedule**: 84% cost reduction from 10-min schedule

## Security

### Sensitive Data Handling
- API keys in environment variables
- Sanitization in error logs
- No credentials in code
- IAM roles for AWS services

### Access Control
- Lambda execution role
- DynamoDB full access
- Translate full access
- S3 read/write for packages

## Known Limitations

1. **Redis Cache**: Implemented but unused
2. **BigKinds Fallback**: Article handler has no fallback
3. **Rate Limiting**: 1s delay (could be optimized)
4. **Translation Batch**: Sequential (not parallel)
5. **Search**: Full table scan (no GSI usage)

## Future Improvements

1. Enable Redis caching for translations
2. Parallel translation processing
3. Use DynamoDB GSI for search
4. Add retry logic for failed translations
5. Implement exponential backoff for API calls
