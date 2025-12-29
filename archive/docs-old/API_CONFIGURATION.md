# API Configuration

## BigKinds API

### Base URL
```
https://tools.kinds.or.kr
```

### API Key (Seoul Economic Daily Only)
```
254bec69-1c13-470f-904a-c4bc9e46cc80
```

### Previous API Key (All Sources)
```
5bf1dc66-79f7-4788-9593-be209e4472e3
```

### Endpoints

#### News Search
- **URL**: `POST https://tools.kinds.or.kr/search/news`
- **Required Parameters**:
  - `access_key`: API key
  - `argument.query`: Search query
  - `argument.published_at.from`: Start date (YYYY-MM-DD)
  - `argument.published_at.until`: End date (YYYY-MM-DD)
  - `argument.fields`: Array (can be empty `[]`)

#### Example Request
```json
{
  "access_key": "254bec69-1c13-470f-904a-c4bc9e46cc80",
  "argument": {
    "query": "AI",
    "published_at": {
      "from": "2024-01-01",
      "until": "2024-01-15"
    },
    "return_from": 0,
    "return_size": 10,
    "sort": {"date": "desc"},
    "fields": []
  }
}
```

#### Example Response
```json
{
  "result": 0,
  "return_object": {
    "total_hits": 17325,
    "documents": [
      {
        "news_id": "01500501.20240114162904001",
        "title": "기사 제목",
        "published_at": "2024-01-14T00:00:00.000+09:00",
        "provider": "대구일보"
      }
    ]
  }
}
```

## AWS Services

### AWS Translate
- **Region**: us-east-1
- **Authentication**: IAM Role (Lambda execution role)
- **Permissions**: TranslateFullAccess

### ElastiCache (Redis)
- **Host**: seodaily-eng-dev-us-east-1.voovfm.0001.use1.cache.amazonaws.com
- **Port**: 6379
- **Connection Timeout**: 2 seconds
- **Socket Timeout**: 2 seconds
- **TTL**: 604800 seconds (7 days)

### API Gateway
- **URL**: https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
- **Endpoints**:
  - `POST /api/search` - Search news articles
  - `POST /api/article` - Get article details

### Lambda Functions
- **seodaily-eng-search-dev**
  - Runtime: Python 3.11
  - Memory: 512 MB
  - Timeout: 30 seconds
  - Handler: handlers.search_handler.lambda_handler

- **seodaily-eng-article-dev**
  - Runtime: Python 3.11
  - Memory: 512 MB
  - Timeout: 30 seconds
  - Handler: handlers.article_handler.lambda_handler

## HTTP Client Configuration

### Lambda Environment
- **Client**: aiohttp 3.9.1
- **Reason**: httpx has DNS resolution issues in Lambda
- **Timeout**: 30 seconds

### Local Development
- **Client**: httpx or aiohttp
- **Timeout**: 30 seconds

## Important Notes

1. **fields parameter is required**: Always include `"fields": []` in BigKinds API requests
2. **Date format**: YYYY-MM-DD (e.g., "2024-01-01")
3. **Redis failures are graceful**: Cache misses don't break the service
4. **Translation failures**: Fall back to original text
5. **Rate limiting**: Be mindful of API call frequency

## Testing

### Test BigKinds API
```bash
curl -s -X POST https://tools.kinds.or.kr/search/news \
  -H "Content-Type: application/json" \
  -d '{
    "access_key":"254bec69-1c13-470f-904a-c4bc9e46cc80",
    "argument":{
      "query":"AI",
      "published_at":{"from":"2024-01-01","until":"2024-01-15"},
      "fields":[]
    }
  }'
```

### Test Lambda Function
```bash
curl -s -X POST https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query":"AI",
    "filters":{
      "published_from":"2024-01-01",
      "published_until":"2024-01-15",
      "providers":[],
      "categories":[]
    },
    "page":1,
    "page_size":2
  }'
```
