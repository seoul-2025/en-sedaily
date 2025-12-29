# SEOdaily-ENG 개발 대화 정리

**날짜**: 2025년 12월 3일  
**도구**: Amazon Q Developer  
**프로젝트**: SEOdaily-ENG (서울경제 영문 뉴스 자동 번역 플랫폼)

---

## 1. 프로젝트 전체 분석

### 요청 내용
프로젝트의 모든 코드와 중요 파일을 하나씩 읽고 파악해달라는 요청

### 분석 결과

#### 아키텍처 (3-Tier Serverless)
```
Frontend (Next.js 14)
    ↓
Backend (AWS Lambda + Python)
    ↓
Data & Services (DynamoDB, AWS Translate, BigKinds API)
```

#### 핵심 구성요소
- **Lambda Functions**: 3개 (search, article, collector)
- **DynamoDB Tables**: 2개 (articles, metadata)
- **EventBridge**: 매시 48분 자동 실행
- **CloudFront + S3**: 정적 사이트 호스팅

#### 현재 상태
- 총 기사: 1,475+개
- 수집 주기: 매시 48분 (KST 기준)
- 월 비용: ~$289
- 도메인: https://en.sedaily.ai

---

## 2. 기사 원본 링크 저장 로직 분석

### 요청 내용
기사 정보 수집과 DynamoDB 저장 과정에서 기사 원본 링크가 어떻게 저장되는지 코드 로직 전체 설명 요청

### 분석된 데이터 흐름

```
EventBridge (매시 48분)
  → article_collector.py
  → bigkinds_client.py (get_article_detail)
  → Article 객체 생성 (original_link 설정)
  → dynamodb_client.py (save_article)
  → DynamoDB 저장
```

### 핵심 코드 위치

#### 1단계: Article Collector (article_collector.py, Line 138-145)
```python
batch_articles = await bigkinds_client.get_article_detail(
    news_ids=batch_ids,
    fields=[
        "news_id", "title", "content", "published_at",
        "provider_name", "category", "byline",
        "provider_link_page",  # ← 원본 링크 필드 요청
        "images", "images_caption"
    ]
)
```

#### 2단계: BigKinds Client (bigkinds_client.py, Line 245-248)
```python
original_link = doc.get("provider_link_page") or doc.get("news_url")
if original_link and original_link.startswith("http://"):
    original_link = original_link.replace("http://", "https://", 1)
```

**처리 로직**:
1. 우선순위: `provider_link_page` → `news_url` (fallback)
2. HTTP → HTTPS 자동 변환

#### 3단계: DynamoDB 저장 (dynamodb_client.py, Line 28-43)
```python
item = {
    'news_id': news_id,
    'original_link': article.get('original_link'),
    # ... 기타 필드
}
response = self.table.put_item(Item=item)
```

---

## 3. "View original article →" 링크 연결 분석

### 요청 내용
기사 본문 페이지에서 "View original article →" 텍스트에 첨부되는 링크가 어떤 방식으로 가져오는지 분석 요청

### 분석된 데이터 흐름

```
사용자 클릭 (/article?id=xxx)
  → article/page.tsx (프론트엔드)
  → fetchArticleDetail(articleId) (utils/api.ts)
  → GET /api/article/{articleId} (API Gateway)
  → article_handler.py (Lambda)
  → DynamoDB get_article(article_id)
  → JSON 응답 (original_link 포함)
  → <a href={article.original_link}> 렌더링
```

### 핵심 코드 위치

#### Frontend (article/page.tsx, Line 169-178)
```typescript
{article.original_link && (
  <footer className="mt-12 pt-6 border-t border-gray-200">
    <a
      href={article.original_link}  // ← 여기서 사용
      target="_blank"
      rel="noopener noreferrer"
    >
      View original article →
    </a>
  </footer>
)}
```

#### Backend (article_handler.py, Line 95-105)
```python
return ArticleDetailResponse(
    original_link=cached_article.get('original_link'),  # ← DynamoDB에서 가져옴
    # ... 기타 필드
)
```

---

## 4. 긴 링크 생성 문제 발견 및 해결

### 문제 발견
`https://www.sedaily.com/NewsView/(news_id)` 형태의 긴 링크가 생성되고 있었음

### 원인 분석
`batch_fix_links.py`와 `fix_all_links.py` 스크립트가 DynamoDB의 모든 `original_link`를 강제로 news_id 기반 URL로 변경했음

```python
# 문제의 코드 (batch_fix_links.py, Line 30)
new_link = f"https://www.sedaily.com/NewsView/{news_id}"
```

### 해결 방법

#### Option 1: 문제 스크립트 비활성화 ✅
```bash
mv batch_fix_links.py batch_fix_links.py.DISABLED
mv fix_all_links.py fix_all_links.py.DISABLED
```

#### Option 2: 기존 기사 링크 복구
BigKinds API에서 `provider_link_page` 필드를 다시 가져와 업데이트 시도

---

## 5. BigKinds API provider_link_page 필드 문제 해결

### 문제 상황
BigKinds API에서 `provider_link_page` 필드가 `None`으로 반환됨

### 원인 발견
`response_validator.py`의 `validate_and_sanitize_bigkinds_detail` 함수에서 `provider_link_page` 필드가 **누락**되어 있었음

### 해결 코드 (response_validator.py)
```python
# 수정 전: provider_link_page 필드 없음
sanitized_doc = {
    'news_id': doc.get('news_id', ''),
    'title': doc.get('title', ''),
    # ... provider_link_page 누락
}

# 수정 후: provider_link_page 필드 추가
sanitized_doc = {
    'news_id': doc.get('news_id', ''),
    'title': doc.get('title', ''),
    'provider_link_page': doc.get('provider_link_page', ''),  # ← 추가
    # ...
}
```

### 테스트 결과
```
Raw API Response: "provider_link_page": "http://www.sedaily.com/NewsView/2H1L4MR7OB"
우리 코드 처리 후: "https://www.sedaily.com/NewsView/2H1L4MR7OB" (HTTPS 변환됨)
```

---

## 6. Lambda 배포 및 DynamoDB 대량 업데이트

### Lambda 배포
```bash
./deploy.sh
# 결과: article_collector Lambda 업데이트 완료
```

### DynamoDB 대량 업데이트 실행
BigKinds API에서 짧은 링크를 가져와 기존 기사들의 `original_link` 업데이트

### 업데이트 결과
| 항목 | 수량 | 비율 |
|------|------|------|
| 총 기사 | 1,578개 | 100% |
| 성공 | 1,536개 | 97.3% |
| 실패 | 41개 | 2.7% |
| 스킵 | 0개 | 0% |

### 링크 형태 변경
- **이전**: `https://www.sedaily.com/NewsView/02100311.20251203092404001` (긴 링크)
- **이후**: `https://www.sedaily.com/NewsView/2H1L4MR7OB` (짧은 링크)

---

## 7. 최종 결과 확인

### API 테스트
```bash
curl "https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/article/04100608.20251203105202001"
```

**응답**:
```json
{
  "original_link": "https://www.sedaily.com/NewsView/2H1L4MR7OB"
}
```

### 향후 자동 처리 확인
새로 수집되는 모든 기사는 자동으로 짧은 링크로 저장됨

**확인 코드** (article_collector.py, Line 189):
```python
'original_link': article.original_link  # BigKinds API의 provider_link_page 사용
```

---

## 주요 변경 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `backend/utils/response_validator.py` | `provider_link_page` 필드 추가 |
| `backend/config.py` | `aws_region` 필드 추가 |
| `batch_fix_links.py` | `.DISABLED`로 이름 변경 |
| `fix_all_links.py` | `.DISABLED`로 이름 변경 |
| `scripts/restore_short_links.py` | 신규 생성 (링크 복구 스크립트) |
| `scripts/test_provider_link.py` | 신규 생성 (테스트 스크립트) |
| `scripts/update_all_links.py` | 신규 생성 (대량 업데이트 스크립트) |

---

## 결론 및 권장사항

### ✅ 해결된 문제
1. BigKinds API `provider_link_page` 필드 활용 가능
2. response_validator 누락 문제 해결
3. Lambda 배포 완료
4. 기존 기사 97.3% 짧은 링크로 업데이트 완료

### 🚀 앞으로의 동작
- **새 기사**: 자동으로 짧은 링크 저장
- **기존 기사**: 97.3%가 짧은 링크로 변경됨
- **수동 작업**: 더 이상 필요 없음

### ⚠️ 주의사항
- `batch_fix_links.py.DISABLED` 절대 실행 금지
- `fix_all_links.py.DISABLED` 절대 실행 금지
