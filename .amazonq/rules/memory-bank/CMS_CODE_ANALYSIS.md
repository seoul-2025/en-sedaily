# CMS Code Analysis - Complete Codebase

**Last Updated**: 2025-12-05
**Status**: ✅ Production Deployed

## 프로젝트 구조

```
cms/
├── src/
│   ├── app/
│   │   ├── page.tsx              # 홈 (리다이렉트)
│   │   ├── layout.tsx            # 루트 레이아웃
│   │   ├── globals.css           # Tailwind CSS
│   │   ├── articles/
│   │   │   └── page.tsx          # News ID 입력 페이지
│   │   └── edit/
│   │       └── page.tsx          # 기사 수정 페이지
│   ├── components/               # (비어있음)
│   └── utils/                    # (비어있음)
├── .env.local                    # API URL 설정
├── next.config.js                # Static export 설정
├── package.json                  # 의존성
├── tailwind.config.ts            # Tailwind 설정
├── tsconfig.json                 # TypeScript 설정
└── update_article.py             # 로컬 테스트 스크립트
```

---

## Frontend 코드 분석

### 1. page.tsx (홈페이지)

**파일**: `src/app/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  
  useEffect(() => {
    router.push('/articles');
  }, [router]);

  return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
}
```

**기능**:
- 자동으로 `/articles`로 리다이렉트
- 로딩 메시지 표시

---

### 2. layout.tsx (루트 레이아웃)

**파일**: `src/app/layout.tsx`

```typescript
import './globals.css';

export const metadata = {
  title: 'SEOdaily CMS',
  description: 'Content Management System',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}
```

**기능**:
- 메타데이터 설정
- 전역 스타일 적용
- 배경색: `bg-gray-50`

---

### 3. articles/page.tsx (News ID 입력)

**파일**: `src/app/articles/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search } from 'lucide-react';

export default function ArticlesPage() {
  const [newsId, setNewsId] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newsId.trim()) {
      router.push(`/edit?id=${newsId.trim()}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold mb-2 text-center">Article Editor</h1>
          <p className="text-gray-600 mb-8 text-center">Enter a news ID to edit an article</p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="newsId" className="block text-sm font-medium text-gray-700 mb-2">
                News ID
              </label>
              <input
                id="newsId"
                type="text"
                value={newsId}
                onChange={(e) => setNewsId(e.target.value)}
                placeholder="e.g., 02100311.20251205131222001"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <button
              type="submit"
              disabled={!newsId.trim()}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
            >
              <Search className="w-5 h-5" />
              Find & Edit Article
            </button>
          </form>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">How to find News ID:</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Visit <a href="https://en.sedaily.ai" target="_blank" className="underline">en.sedaily.ai</a></li>
              <li>Click on any article</li>
              <li>Copy the ID from the URL (after ?id=)</li>
              <li>Paste it here to edit</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
```

**기능**:
- News ID 입력 폼
- 유효성 검사 (빈 값 방지)
- `/edit?id={newsId}` 로 이동
- 사용 방법 안내

**UI 요소**:
- 중앙 정렬 카드 레이아웃
- Search 아이콘 (lucide-react)
- 파란색 버튼 (bg-blue-600)
- 도움말 박스 (bg-blue-50)

---

### 4. edit/page.tsx (기사 수정)

**파일**: `src/app/edit/page.tsx`

```typescript
'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

function EditArticleContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get('id');
  
  const [article, setArticle] = useState<any>(null);
  const [form, setForm] = useState({
    title_en: '',
    content_en: '',
    category: '',
    meta_description: '',
    keywords: '',
    hashtags: ''
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    
    fetch(`${API_URL}/api/article/${id}`)
      .then(res => res.json())
      .then(data => {
        setArticle(data);
        setForm({
          title_en: data.title || '',
          content_en: data.content || '',
          category: data.category || '',
          meta_description: data.meta_description || '',
          keywords: data.keywords || '',
          hashtags: data.hashtags || ''
        });
      });
  }, [id]);

  async function handleSave() {
    if (!id) return;
    setSaving(true);
    
    try {
      // Direct DynamoDB update via Python script approach
      const response = await fetch(`${API_URL}/api/update-article`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          news_id: id,
          updates: {
            title_en: form.title_en,
            content_en: form.content_en,
            category: form.category,
            meta_description: form.meta_description,
            keywords: form.keywords,
            hashtags: form.hashtags
          }
        })
      });
      
      if (response.ok) {
        alert('✅ Article updated successfully!');
      } else {
        throw new Error('Update failed');
      }
    } catch (error) {
      alert('❌ Failed to save. Please try again.');
      console.error(error);
    } finally {
      setSaving(false);
    }
  }

  if (!id) return <div className="p-8">No article ID provided</div>;
  if (!article) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Edit Article</h1>
          <div className="flex gap-2">
            <button 
              onClick={() => router.push('/articles')} 
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button 
              onClick={handleSave} 
              disabled={saving}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">News ID</label>
            <input
              type="text"
              value={article.news_id}
              disabled
              className="w-full px-4 py-2 border rounded bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Title</label>
            <input
              type="text"
              value={form.title_en}
              onChange={e => setForm({...form, title_en: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Category</label>
            <select
              value={form.category}
              onChange={e => setForm({...form, category: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            >
              <option value="경제">경제</option>
              <option value="IT_과학">IT_과학</option>
              <option value="정치">정치</option>
              <option value="사회">사회</option>
              <option value="문화">문화</option>
              <option value="스포츠">스포츠</option>
              <option value="국제">국제</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Content</label>
            <textarea
              value={form.content_en}
              onChange={e => setForm({...form, content_en: e.target.value})}
              rows={20}
              className="w-full px-4 py-2 border rounded font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Meta Description</label>
            <textarea
              value={form.meta_description}
              onChange={e => setForm({...form, meta_description: e.target.value})}
              rows={3}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Keywords</label>
            <input
              type="text"
              value={form.keywords}
              onChange={e => setForm({...form, keywords: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Hashtags</label>
            <input
              type="text"
              value={form.hashtags}
              onChange={e => setForm({...form, hashtags: e.target.value})}
              className="w-full px-4 py-2 border rounded"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EditArticle() {
  return (
    <Suspense fallback={<div className="p-8">Loading...</div>}>
      <EditArticleContent />
    </Suspense>
  );
}
```

**기능**:
- URL 쿼리 파라미터에서 `id` 추출
- `GET /api/article/{id}` 로 기사 조회
- 폼 상태 관리 (6개 필드)
- `POST /api/update-article` 로 저장
- 성공/실패 알림

**수정 가능 필드**:
1. `title_en` - 영문 제목
2. `content_en` - 영문 본문 (20줄 textarea)
3. `category` - 카테고리 (select)
4. `meta_description` - SEO 메타 설명 (3줄 textarea)
5. `keywords` - SEO 키워드
6. `hashtags` - SEO 해시태그

**UI 요소**:
- Cancel 버튼 (회색 테두리)
- Save 버튼 (파란색, disabled 상태)
- News ID (읽기 전용, 회색 배경)
- 모든 입력 필드 (흰색 배경)

---

## Backend 코드 분석

### Lambda Handler

**파일**: `backend/handlers/cms_update_handler.py`

```python
"""
CMS Update Handler
Direct DynamoDB update for CMS article editing
"""
import json
import logging
from datetime import datetime
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


def lambda_handler(event, context):
    """Update article directly in DynamoDB"""
    
    try:
        body = json.loads(event['body'])
        news_id = body['news_id']
        updates = body['updates']
        
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        # Add fields to update
        updatable = ['title_en', 'content_en', 'category', 'meta_description', 'keywords', 'hashtags']
        for field in updatable:
            if field in updates:
                update_expr += f", {field} = :{field}"
                expr_values[f':{field}'] = updates[field]
        
        # Update DynamoDB
        response = table.update_item(
            Key={'news_id': news_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ReturnValues='ALL_NEW'
        )
        
        logger.info(f"✅ Updated article {news_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'message': 'Article updated successfully',
                'article': response['Attributes']
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"❌ Update failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
```

**기능**:
- DynamoDB `update_item` 직접 사용
- 동적 UpdateExpression 생성
- `updated_at` 자동 추가
- CORS 헤더 포함
- 에러 로깅

**패턴**: `update_all_to_short_links.py`와 동일

---

### 로컬 테스트 스크립트

**파일**: `cms/update_article.py`

```python
#!/usr/bin/env python3
"""
CMS Article Update Script
Updates a single article in DynamoDB with edited content
"""
import boto3
import sys
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('seodaily-eng-articles-dev')


def update_article(news_id: str, updates: dict):
    """Update article in DynamoDB"""
    
    # Build update expression
    update_expr = "SET updated_at = :updated_at"
    expr_values = {':updated_at': datetime.utcnow().isoformat()}
    
    # Add fields to update
    updatable = ['title_en', 'content_en', 'category', 'meta_description', 'keywords', 'hashtags']
    for field in updatable:
        if field in updates:
            update_expr += f", {field} = :{field}"
            expr_values[f':{field}'] = updates[field]
    
    # Update DynamoDB
    response = table.update_item(
        Key={'news_id': news_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    
    return response['Attributes']


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_article.py <news_id>")
        sys.exit(1)
    
    news_id = sys.argv[1]
    
    # Example: Update title
    updates = {
        'title_en': 'Updated Title',
        'content_en': 'Updated content...',
        'category': '경제'
    }
    
    result = update_article(news_id, updates)
    print(f"✅ Updated {news_id}")
    print(f"Title: {result.get('title_en')}")
```

**사용법**:
```bash
python update_article.py 02100311.20251205131222001
```

---

## 설정 파일

### 1. package.json

```json
{
  "name": "seodaily-cms",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3001",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.0",
    "react": "^18",
    "react-dom": "^18",
    "@tanstack/react-table": "^8.11.0",
    "react-hook-form": "^7.49.0",
    "date-fns": "^3.0.0",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.4.0",
    "eslint": "^8",
    "eslint-config-next": "14.2.0"
  }
}
```

**포트**: 3001 (dev 서버)

---

### 2. next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true }
};

module.exports = nextConfig;
```

**설정**:
- Static export (S3 배포용)
- 이미지 최적화 비활성화

---

### 3. .env.local

```bash
NEXT_PUBLIC_API_URL=https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
```

**환경 변수**:
- API Gateway URL

---

### 4. tailwind.config.ts

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {} },
  plugins: [],
};
export default config;
```

**설정**:
- 기본 Tailwind 설정
- 커스텀 테마 없음

---

### 5. globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**스타일**:
- Tailwind CSS만 사용
- 커스텀 CSS 없음

---

## 데이터 흐름

### 1. 기사 조회

```
사용자 입력 (News ID)
  ↓
/edit?id={news_id}
  ↓
GET /api/article/{id}
  ↓
DynamoDB.get_item()
  ↓
기사 데이터 반환
  ↓
폼에 표시
```

### 2. 기사 수정

```
사용자 수정 (폼)
  ↓
Save 버튼 클릭
  ↓
POST /api/update-article
  {
    news_id: "...",
    updates: {
      title_en: "...",
      content_en: "...",
      category: "...",
      meta_description: "...",
      keywords: "...",
      hashtags: "..."
    }
  }
  ↓
Lambda: cms_update_handler
  ↓
DynamoDB.update_item()
  ↓
성공 응답
  ↓
알림 표시
```

---

## API 엔드포인트

### 1. 기사 조회

**Endpoint**: `GET /api/article/{id}`
**Lambda**: `seodaily-eng-article-dev` (기존)
**Response**:
```json
{
  "news_id": "...",
  "title": "...",
  "content": "...",
  "category": "...",
  "meta_description": "...",
  "keywords": "...",
  "hashtags": "..."
}
```

### 2. 기사 수정

**Endpoint**: `POST /api/update-article`
**Lambda**: `seodaily-eng-cms-update-dev` (신규)
**Request**:
```json
{
  "news_id": "02100311.20251205131222001",
  "updates": {
    "title_en": "Updated Title",
    "content_en": "Updated content...",
    "category": "경제",
    "meta_description": "...",
    "keywords": "...",
    "hashtags": "..."
  }
}
```
**Response**:
```json
{
  "message": "Article updated successfully",
  "article": { ... }
}
```

---

## 배포 정보

### Lambda
- **Function**: `seodaily-eng-cms-update-dev`
- **Runtime**: Python 3.11
- **Memory**: 512MB
- **Timeout**: 30s
- **Handler**: `handlers.cms_update_handler.lambda_handler`

### API Gateway
- **API ID**: 7w5nco7xn4
- **Stage**: dev
- **Resource**: `/api/update-article`
- **Method**: POST, OPTIONS (CORS)

### CloudFront
- **Distribution ID**: EAEB9I2CA0NDK
- **Domain**: https://enadmin.sedaily.ai
- **Origin**: S3 (seodaily-eng-cms-dev-us-east-1)

### S3
- **Bucket**: seodaily-eng-cms-dev-us-east-1
- **Content**: Static export (out/ 폴더)

---

## 주요 특징

### 1. 단순성
- 페이지 3개만 (home, articles, edit)
- 컴포넌트 없음 (모두 인라인)
- 유틸리티 없음

### 2. 빠른 로딩
- News ID 입력 방식
- 목록 로딩 없음
- 필요한 기사만 조회

### 3. 직접 업데이트
- DynamoDB `update_item` 직접 사용
- 중간 API 없음
- `update_all_to_short_links.py` 패턴

### 4. 실시간 반영
- 저장 즉시 DynamoDB 업데이트
- en.sedaily.ai에서 새로고침 시 반영

---

## 의존성

### Production
- next: 14.2.0
- react: ^18
- react-dom: ^18
- lucide-react: ^0.344.0 (아이콘)
- @tanstack/react-table: ^8.11.0 (미사용)
- react-hook-form: ^7.49.0 (미사용)
- date-fns: ^3.0.0 (미사용)

### Development
- typescript: ^5
- tailwindcss: ^3.4.0
- eslint: ^8

**미사용 패키지**: react-table, react-hook-form, date-fns (제거 가능)

---

## 빌드 결과

```
Route (app)                              Size     First Load JS
┌ ○ /                                    412 B          87.4 kB
├ ○ /_not-found                          875 B          87.9 kB
├ ○ /articles                            1.61 kB        88.6 kB
└ ○ /edit                                1.57 kB        88.6 kB
+ First Load JS shared by all            87 kB
```

**총 크기**: 87 kB (매우 가벼움)

---

## 보안

### CORS
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: POST,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

### 인증
- ❌ 현재 없음
- ⏳ AWS Cognito 추가 예정

---

## 향후 개선

1. 미사용 패키지 제거 (react-table, react-hook-form, date-fns)
2. AWS Cognito 인증 추가
3. 수정 이력 추적
4. 에러 처리 개선 (toast 알림)
5. 로딩 스피너 추가
