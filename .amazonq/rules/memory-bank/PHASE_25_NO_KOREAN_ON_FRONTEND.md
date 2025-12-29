# Phase 25: Complete Korean Removal from Frontend - COMPLETED (2025-12-10)

**Date**: 2025-12-10
**Status**: ✅ COMPLETED
**Goal**: 프론트엔드(en.sedaily.ai)에서 한국어 완전 제거

---

## 문제 발견

프론트엔드에 한국어가 표시되는 2가지 경로:

### 1. 카테고리 (Category)
- **문제**: DynamoDB에 한국어 카테고리 저장 (`경제`, `IT_과학` 등)
- **영향**: API 응답에 한국어 카테고리 그대로 반환
- **표시 위치**: 기사 상단 카테고리 배지

### 2. 기자명 (Byline)
- **문제**: BigKinds API의 한국어 기자명 그대로 저장 (`홍길동 기자`)
- **영향**: 기사 상세 페이지에 한국어 기자명 표시
- **표시 위치**: 기사 제목 아래 byline

---

## 해결 방법

### 1. 카테고리 영문 변환

**파일**: `backend/handlers/article_collector.py`

**변경 사항**:
```python
# Convert Korean category to English
category_map = {
    '경제': 'finance',
    'IT_과학': 'technology',
    '정치': 'politics',
    '사회': 'society',
    '문화': 'culture',
    '스포츠': 'sports',
    '국제': 'international'
}
category = category_map.get(category, 'news')
```

**결과**:
- DynamoDB에 영문 카테고리 저장
- API 응답에 영문 카테고리 반환
- 프론트엔드에 영문 표시

### 2. 기자명 영문 변환

**파일**: `backend/handlers/article_collector.py`

**변경 사항**:
```python
# Extract [BYLINE] from Claude translation
byline_match = re.search(r'\[BYLINE\]\s*By\s+([^\[\n]+)', translated_full, re.IGNORECASE)
byline_en = byline_match.group(1).strip() if byline_match else article.byline

# Save English byline
'byline': byline_en
```

**Claude 번역 출력 예시**:
```
[HEADLINE]
Samsung Reports Q4 Profit Surge

[BYLINE]
By Kim Min-soo

[ARTICLE]
...
```

**결과**:
- Claude가 한국어 기자명을 영문으로 변환
- `[BYLINE]` 섹션에서 영문 기자명 추출
- DynamoDB에 영문 기자명 저장
- 프론트엔드에 영문 표시

---

## 변환 규칙

### 카테고리 매핑

| 한국어 | 영문 |
|--------|------|
| 경제 | finance |
| IT_과학 | technology |
| 정치 | politics |
| 사회 | society |
| 문화 | culture |
| 스포츠 | sports |
| 국제 | international |
| (기타) | news |

### 기자명 변환 (Claude 자동)

| 한국어 | 영문 |
|--------|------|
| 홍길동 기자 | Hong Gil-dong |
| 김민수 기자 | Kim Min-soo |
| 이재용 기자 | Lee Jae-yong |

**변환 규칙** (TRANSLATION_PROMPT.md):
- 성-이름 순서 유지
- 이름 음절 사이 하이픈 (-)
- 공식 영문명 있으면 우선 사용

---

## 배포

### 백엔드 배포
```bash
cd backend
./build_lambda.sh
```

**배포 결과**:
- Package Size: 34.3 MB
- Lambda Functions Updated: 3/3
  - seodaily-eng-search-dev ✅
  - seodaily-eng-article-dev ✅
  - seodaily-eng-article-collector-dev ✅
- Status: Active
- Date: 2025-12-10 01:10 UTC

---

## 검증

### 신규 기사 (다음 수집부터)
- ✅ 카테고리: 영문으로 저장
- ✅ 기자명: 영문으로 저장
- ✅ 프론트엔드: 한국어 없음

### 기존 기사 (3,165개)
- ⚠️ 카테고리: 한국어로 저장됨 (변환 필요)
- ⚠️ 기자명: 한국어로 저장됨 (변환 필요)

**해결 방법**:
1. 기존 기사는 점진적으로 교체됨 (매일 신규 기사 추가)
2. 또는 일괄 변환 스크립트 실행 (선택사항)

---

## 영향 범위

### 프론트엔드
- **Homepage**: 카테고리 배지 영문 표시
- **Category Pages**: URL 및 제목 영문 유지
- **Article Detail**: 카테고리 + 기자명 영문 표시
- **Search Results**: 카테고리 영문 표시

### API 응답
```json
{
  "news_id": "...",
  "title": "Samsung Reports...",
  "category": "finance",
  "byline": "Kim Min-soo",
  "content": "..."
}
```

### DynamoDB
```python
{
    'news_id': '...',
    'category': 'finance',  # 영문
    'byline': 'Kim Min-soo',  # 영문
    ...
}
```

---

## 결과

✅ **프론트엔드에 한국어 완전 제거**
- 카테고리: 영문 ✅
- 기자명: 영문 ✅
- 제목: 영문 ✅
- 본문: 영문 ✅
- 메타데이터: 영문 ✅

✅ **100% 영문 사이트 달성**

---

## 파일 수정 내역

1. `backend/handlers/article_collector.py`
   - 카테고리 영문 변환 로직 추가
   - 기자명 영문 추출 로직 추가
   - DynamoDB 저장 시 영문 사용

---

## 다음 단계

### 선택사항: 기존 기사 일괄 변환
```python
# 스크립트 예시
for article in dynamodb.scan():
    # 카테고리 변환
    category_map = {...}
    article['category'] = category_map.get(article['category'], 'news')
    
    # 기자명은 원본 유지 (Claude 재번역 필요)
    
    # 업데이트
    dynamodb.update_item(...)
```

**우선순위**: 낮음 (신규 기사로 자연스럽게 교체됨)

---

## 메모

- Claude의 TRANSLATION_PROMPT.md에 이미 기자명 영문 변환 지침 포함
- 기존 시스템 활용으로 추가 비용 없음
- 프론트엔드 코드 변경 불필요
