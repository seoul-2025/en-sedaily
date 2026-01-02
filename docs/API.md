## API Endpoints

### Search Endpoints
```
GET  /api/search
     Query Parameters:
     - query: string (search term)
     - category: string (optional)
     - from_date: string (ISO format, optional)
     - until_date: string (ISO format, optional)
     - limit: int (default: 25, max: 100)

     Response:
     {
       "articles": [
         {
           "news_id": "01166872356",
           "title_en": "Samsung Reports Record Q4 Earnings",
           "content_en": "Samsung Electronics...",
           "category": "finance",
           "published_date": "2025-12-22T10:30:00+09:00",
           "byline": "By Tae-gyu Lee",
           "original_link": "https://www.sedaily.com/NewsView/2H1L4MR7OB",
           "meta_description": "...",
           "keywords": ["Samsung", "Earnings", "Q4"],
           "hashtags": ["#Samsung", "#TechStocks"]
         }
       ],
       "total": 156,
       "query": "Samsung"
     }
```

### Article Endpoints
```
GET  /api/article/{news_id}
     Legacy endpoint (still supported for backward compatibility)
     Response:
     {
       "news_id": "02100311.20251223092834001",
       "slug": "samsung-q4-earnings-beat-expectations",
       "title": "삼성전자, 4분기 실적 발표",
       "title_en": "Samsung Reports Record Q4 Earnings",
       "content": "삼성전자가...",
       "content_en": "Samsung Electronics announced...",
       "category": "경제",
       "published_at": "2025-12-23T09:28:34.000+09:00",
       "byline": "By Tae-gyu Lee",
       "original_link": "https://www.sedaily.com/NewsView/2H1L4MR7OB",
       "meta_description": "Samsung Electronics reports record Q4 earnings with...",
       "keywords": ["Samsung", "Quarterly Earnings", "Technology"],
       "hashtags": ["#Samsung", "#Q4Earnings", "#TechStocks"],
       "created_at": "2025-12-23T10:00:00Z",
       "updated_at": "2025-12-23T10:00:00Z"
     }

GET  /api/article/by-slug/{slug}
     SEO-friendly endpoint (preferred)
     Example: /api/article/by-slug/samsung-q4-earnings-beat-expectations
     Response: (same as above)
```

### CMS Endpoints
```
POST /api/update-article
     Body:
     {
       "news_id": "01166872356",
       "title_en": "Updated Title",
       "content_en": "Updated content...",
       "category": "finance",
       "meta_description": "Updated description",
       "keywords": ["keyword1", "keyword2"],
       "hashtags": ["#tag1", "#tag2"]
     }

     Response:
     {
       "success": true,
       "message": "Article updated successfully",
       "news_id": "01166872356"
     }
```

---

