## How It Works

### Automatic Article Collection (Every Hour)

1. **EventBridge Trigger** (Every hour at :48)
   ```
   rate(1 hour) → Lambda Collector
   ```

2. **Collect Today's Articles** (00:00 ~ 23:59 KST)
   ```python
   now = datetime.now()
   from_date = now.replace(hour=0, minute=0, second=0)
   until = from_date + timedelta(days=2)
   ```

3. **BigKinds API Call** (Seoul Economic only)
   ```python
   articles = await bigkinds_api.search_news(
       provider_codes=["0102"],  # Seoul Economic
       from_date=from_date,
       until_date=until,
       fields=["provider_link_page"]
   )
   ```

4. **Deduplication Check**
   ```python
   existing = await dynamodb_client.get_article(news_id)
   if existing:
       # Skip translation, update link only
       continue
   ```

5. **Content Filtering**
   ```python
   if not article.content or not article.content.strip():
       # Skip articles without content
       continue
   ```

6. **AI Translation** (Claude Opus 4.5)
   ```python
   translation = await translator.translate_article(
       title=article.title,
       content=article.content,
       model="claude-opus-4-5-20251101"
   )
   # Returns: HEADLINE, BYLINE, ARTICLE, DISCLAIMER, SEO/AEO
   ```

7. **HTTPS Conversion**
   ```python
   if original_link.startswith("http://"):
       original_link = original_link.replace("http://", "https://", 1)
   ```

8. **Save to DynamoDB**
   ```python
   await dynamodb_client.put_article({
       "news_id": news_id,
       "title_en": translation.headline,
       "content_en": translation.article,
       "byline": translation.byline,
       "meta_description": translation.meta_description,
       "keywords": translation.keywords,
       "hashtags": translation.hashtags
   })
   ```

### Frontend Display (Server-Side Rendering)

1. **User Visits Page**
   ```
   Browser → Nginx → PM2 → Next.js SSR
   ```

2. **ISR Cache Check**
   ```typescript
   // Main page: revalidate every 5 minutes
   export const revalidate = 300;

   // Category page: revalidate every 10 minutes
   export const revalidate = 600;

   // Article page: revalidate every 1 hour
   export const revalidate = 3600;
   ```

3. **Server-Side Data Fetch**
   ```typescript
   const articles = await fetchLatestArticles();
   ```

4. **API Gateway → DynamoDB**
   ```
   Next.js → API Gateway → Lambda → DynamoDB
   ```

5. **Render HTML on Server**
   ```
   Next.js SSR → HTML with data → Send to client
   ```

6. **Client-Side Hydration**
   ```
   React hydrates the page for interactivity
   ```

7. **Article Rotation**
   - **Featured**: articles[0] (newest)
   - **Top Stories**: articles[1-5]
   - **Category Hero**: articles[0] per category
   - **Automatic**: Updates when new article collected

---

