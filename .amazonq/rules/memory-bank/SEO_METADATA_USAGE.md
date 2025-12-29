# SEO Metadata Usage Guide

## Overview
Claude Opus 4.5 번역 시 자동으로 생성되는 SEO/AEO 메타데이터가 DynamoDB에 저장됩니다.

## DynamoDB Fields

새로 추가된 필드:
- `meta_description`: Google Search Console용 메타 설명 (155자 이내)
- `keywords`: 검색 엔진 색인용 키워드 (5-7개)
- `hashtags`: 소셜 미디어용 해시태그 (5-7개)

## Frontend Usage Example

### 1. Article Detail Page Meta Tags

```typescript
// src/app/article/page.tsx
export async function generateMetadata({ searchParams }): Promise<Metadata> {
  const articleId = searchParams.id;
  const article = await fetchArticleDetail(articleId);
  
  return {
    title: article.title,
    description: article.meta_description || article.content?.substring(0, 160),
    keywords: article.keywords,
    openGraph: {
      title: article.title,
      description: article.meta_description,
    },
    twitter: {
      title: article.title,
      description: article.meta_description,
    }
  };
}
```

### 2. Display Hashtags

```typescript
// Article detail page
{article.hashtags && (
  <div className="flex gap-2 flex-wrap mt-4">
    {article.hashtags.split(',').map((tag, i) => (
      <span key={i} className="text-sm text-blue-600">
        {tag.trim()}
      </span>
    ))}
  </div>
)}
```

### 3. Schema.org Structured Data

```typescript
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'NewsArticle',
  headline: article.title,
  description: article.meta_description,
  keywords: article.keywords,
  // ... other fields
};
```

## API Response Format

```json
{
  "news_id": "02100311.20251204170230001",
  "title": "KOTRA Hosts Global Telecom Giants...",
  "content": "Article content...",
  "meta_description": "KOTRA organized a meeting with global telecom companies...",
  "keywords": "KOTRA, telecom, AI, 6G, Samsung, LG",
  "hashtags": "#KOTRA #Telecom #AI #6G #Samsung"
}
```

## Benefits

1. **Google Search Console**: 최적화된 메타 설명으로 검색 결과 개선
2. **SEO**: 키워드로 검색 엔진 색인 향상
3. **Social Media**: 해시태그로 소셜 미디어 노출 증가
4. **Answer Engines**: Perplexity, ChatGPT 등에서 발견 가능성 향상

## Next Steps (Optional)

1. 프론트엔드 `article/page.tsx`에 메타데이터 적용
2. 소셜 공유 버튼에 해시태그 자동 포함
3. Google Search Console에서 메타 설명 성능 모니터링
