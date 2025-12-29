# SEOdaily-ENG Architecture

## System Overview

SEOdaily-ENG는 BigKinds API를 통해 서울경제 기사를 수집하고, 번역하여 DynamoDB에 저장한 후, 웹사이트에서 표시하는 시스템입니다.

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Article Collection                     │
│                                                               │
│  BigKinds API (서울경제 전용)                                │
│         ↓                                                     │
│  article_collector Lambda (6시간마다)                        │
│         ↓                                                     │
│  AWS Translate (한글 → 영어)                                 │
│         ↓                                                     │
│  검증 & 필터링 (본문 있는 기사만)                            │
│         ↓                                                     │
│  DynamoDB 저장 (seodaily-eng-articles-dev)                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    2. Website Display                        │
│                                                               │
│  사용자 요청                                                  │
│         ↓                                                     │
│  search_handler Lambda (검색)                                │
│         ↓                                                     │
│  DynamoDB 조회 (번역된 기사만)                               │
│         ↓                                                     │
│  article_handler Lambda (상세)                               │
│         ↓                                                     │
│  DynamoDB 조회 (번역된 기사만)                               │
│         ↓                                                     │
│  프론트엔드 표시                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Principles

### 1. BigKinds API = 수집 전용
- **용도**: 서울경제 기사 수집
- **사용처**: article_collector Lambda만 사용
- **주기**: 6시간마다 자동 실행
- **웹사이트**: BigKinds API 직접 호출 안 함

### 2. DynamoDB = 단일 데이터 소스
- **저장**: 번역 완료된 기사만 저장
- **조회**: 모든 웹사이트 요청은 DynamoDB에서만 처리
- **보장**: DynamoDB에 있는 기사 = 본문 있음

### 3. 번역 = 수집 시점에만
- **시점**: article_collector 실행 시
- **방식**: AWS Translate (한글 → 영어)
- **캐싱**: DynamoDB에 영구 저장
- **웹사이트**: 실시간 번역 안 함

## Components

### Backend Lambda Functions

#### 1. article_collector
- **역할**: BigKinds API에서 기사 수집 및 번역
- **실행**: EventBridge (6시간마다)
- **처리**:
  1. BigKinds API 호출 (최근 6시간 기사)
  2. 중복 체크 (DynamoDB)
  3. 번역 (AWS Translate)
  4. 카테고리 추출 (첫 번째 메인 카테고리)
  5. DynamoDB 저장
- **필터링**: 본문 없는 기사 제외

#### 2. search_handler
- **역할**: DynamoDB에서 기사 검색
- **입력**: 날짜 범위, 카테고리
- **출력**: 번역된 기사 목록
- **특징**: BigKinds API 호출 안 함

#### 3. article_handler
- **역할**: DynamoDB에서 기사 상세 조회
- **입력**: news_id
- **출력**: 번역된 기사 전체 내용
- **특징**: BigKinds API 폴백 없음

### Frontend

#### Pages
- **Homepage**: 최근 7일 기사 (DynamoDB)
- **Category Pages**: 카테고리별 기사 (DynamoDB)
- **Article Detail**: 기사 상세 (DynamoDB)
- **Search**: 검색 결과 (DynamoDB)

#### Data Source
- **모든 페이지**: DynamoDB만 사용
- **빌드 시점**: API 호출하여 정적 페이지 생성
- **런타임**: 클라이언트 사이드에서 API 호출

## Database Schema

### DynamoDB Table: seodaily-eng-articles-dev

```
{
  "news_id": "02100311.20251129060222001",  // Primary Key
  "title_ko": "한글 제목",
  "title_en": "English Title",
  "content_ko": "한글 본문",
  "content_en": "English Content",
  "published_at": "2024-11-29T06:02:22.000+09:00",
  "category": "경제",  // 단일 카테고리 (메인만)
  "provider": "서울경제",
  "byline": "기자 이름",
  "original_link": "http://www.sedaily.com/NewsView/...",
  "images": ["/path/to/image.jpg"],
  "images_caption": ["이미지 설명"],
  "translated_at": "2024-11-29T12:00:00.000Z"
}
```

## API Endpoints

### POST /api/search
- **입력**: 날짜 범위, 카테고리, 페이지
- **출력**: 기사 목록 (DynamoDB)
- **응답 시간**: ~200ms

### GET /api/article/{news_id}
- **입력**: news_id
- **출력**: 기사 상세 (DynamoDB)
- **응답 시간**: ~100ms

## Deployment

### Lambda Functions
```bash
cd backend
./build_lambda.sh
```

### Frontend
```bash
cd frontend
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```

## Monitoring

### CloudWatch Logs
- `/aws/lambda/seodaily-eng-search-dev`
- `/aws/lambda/seodaily-eng-article-dev`
- `/aws/lambda/seodaily-eng-article-collector-dev`

### Metrics
- **수집 주기**: 6시간
- **평균 수집 기사**: 10-50개
- **DynamoDB 총 기사**: 67개 (2024-12-01 기준)
- **번역 비용**: ~$2.40/월

## Security

### API Keys
- BigKinds API Key: 환경 변수로 관리
- AWS Credentials: IAM Role 사용

### CORS
- API Gateway: `Access-Control-Allow-Origin: *`
- CloudFront: 모든 origin 허용

## Future Improvements

1. **이미지 최적화**: BigKinds 이미지 서버 URL 확인
2. **검색 기능**: 키워드 검색 (현재는 날짜/카테고리만)
3. **페이지네이션**: 무한 스크롤
4. **관련 기사**: 추천 알고리즘
5. **성능 최적화**: DynamoDB GSI 추가
