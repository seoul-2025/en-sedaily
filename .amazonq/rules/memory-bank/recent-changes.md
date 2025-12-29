# Recent Changes

## 🎉 Project Phase 1 Complete (2025-01-08)

**Status**: ✅ Production Ready
**URL**: https://en.sedaily.ai
**CMS**: https://enadmin.sedaily.ai

All core features implemented and deployed. See `PROJECT_COMPLETION_2025-01-08.md` for full report.

---

## Phase 27.2: Search UI Fix - COMPLETED (2025-01-08)

### Overview
검색 결과 페이지의 기사 상자 색상을 배경색에 맞춰 흰색으로 변경.

### Changes
- ✅ 배경색: `bg-[rgb(50,50,50)]` → `bg-white`
- ✅ 테두리: `border-gray-600` → `border-gray-200`
- ✅ 제목: `text-white` → `text-[var(--color-text)]`
- ✅ 메타: `text-gray-300` → `text-[var(--color-text-muted)]`

### Deployment
- **Date**: 2025-12-10 07:21 UTC
- **Build**: 97.3 kB First Load JS
- **CloudFront**: IBPDX5R41OHDBV80LUW617ZBXC

### Files Modified
1. `frontend/src/app/search/page.tsx`

### Results
- ✅ 검색 결과 페이지 디자인 통일
- ✅ 흰색 배경과 조화
- ✅ 더 깔끔한 UI

---

## Phase 27.1: Thumbnail Image Fix - COMPLETED (2025-01-08)

### Overview
썸네일 이미지가 모든 페이지(홈/카테고리/검색)에서 표시되도록 search_handler.py 수정 및 배포 완료.

### Problem
- ✅ 기사 상세: 이미지 정상 표시
- ❌ 홈페이지 Featured: 이미지 안 나옴
- ❌ 카테고리 Hero: 이미지 안 나옴
- ❌ 검색 결과: 이미지 안 나옴

### Root Cause
`search_handler.py`가 API 응답에 `original_link` 필드를 포함하지 않음

### Solution
- ✅ Backend: search_handler.py에 original_link 필드 추가
- ✅ Frontend: 모든 페이지에 이미지 로직 이미 구현됨
- ✅ Deployment: Lambda 3개 함수 모두 업데이트 완료 (34.3 MB)

### Deployment
- **Date**: 2025-12-10 07:13 UTC
- **Package Size**: 34.3 MB
- **Functions Updated**: 3/3
  - seodaily-eng-search-dev ✅
  - seodaily-eng-article-dev ✅
  - seodaily-eng-article-collector-dev ✅

### Files Modified
1. `backend/handlers/search_handler.py` - original_link 추가

### Results
- ✅ 홈페이지 Featured: 썸네일 이미지 표시
- ✅ 카테고리 Hero: 썸네일 이미지 표시
- ✅ 검색 결과: 썸네일 이미지 표시
- ✅ 모든 페이지에서 이미지 정상 작동

### Status
✅ COMPLETED - All thumbnails now display correctly

---

## Phase 27: Automatic Image Display - COMPLETED (2025-01-08)

### Overview
DynamoDB 저장 정보(`images`, `published_at`)를 활용하여 서울경제 이미지 서버에서 직접 이미지 자동 표시.

### Changes
1. ✅ **Frontend (1 file)**: article/page.tsx - 이미지 URL 자동 생성 로직
2. ✅ **URL Pattern**: `https://newsimg.sedaily.com/{year}/{month}/{day}/{filename}`
3. ✅ **Error Handling**: 이미지 로드 실패 시 원본 링크 폴백
4. ✅ **Caption Display**: images_caption[0] 자동 표시

### Technical Details
- **URL 생성**: `published_at` (날짜) + `images[0]` (파일명)
- **Fallback**: onError 핸들러로 자동 폴백
- **Cost**: $0 (서울경제 이미지 서버 직접 링크)

### Results
- ✅ 이미지 자동 표시
- ✅ 추가 비용 없음
- ✅ 사용자 경험 개선
- ✅ 백엔드 수정 불필요

### Files Modified
1. `frontend/src/app/article/page.tsx`

---

## Phase 26: Naver TV Video Integration - COMPLETED (2025-12-10)

### Overview
CMS에서 네이버 TV 영상 URL 첨부 시 사용자 웹사이트(en.sedaily.ai)에서 기사 하단에 자동재생되는 기능 추가.

### Changes
1. ✅ **Backend (3 files)**: cms_update_handler.py, article_handler.py, dynamodb_client.py
2. ✅ **CMS Frontend (1 file)**: edit/page.tsx with naver_tv_url input field
3. ✅ **User Frontend (2 files)**: article/page.tsx with video player, types/article.ts
4. ✅ **Deployment**: All Lambda functions, CMS, and frontend deployed

### Technical Details
- **DynamoDB**: 14개 필드 (naver_tv_url 추가)
- **URL 변환**: `/v/12345` → `/embed/12345?autoPlay=true`
- **Video Player**: 16:9 responsive iframe with autoplay
- **CMS Lambda**: Updated separately (2025-12-10 05:51 UTC)

### Test Results
- ✅ DynamoDB: `https://tv.naver.com/v/90047457` 저장 확인
- ✅ API: naver_tv_url 정상 반환
- ✅ Frontend: 동영상 플레이어 자동재생 작동
- ✅ Test Article: 02100311.20251210060456001

### Files Modified
1. `backend/handlers/cms_update_handler.py`
2. `backend/handlers/article_handler.py`
3. `backend/clients/dynamodb_client.py`
4. `cms/src/app/edit/page.tsx`
5. `frontend/src/app/article/page.tsx`
6. `frontend/src/types/article.ts`

### Results
- ✅ CMS: 7개 편집 가능 필드 (naver_tv_url 추가)
- ✅ Cost: $0 추가 비용
- ✅ Performance: 영향 없음

---

## Phase 25: Complete Korean Removal from Frontend - COMPLETED (2025-12-10)

### Overview
CMS에서 네이버 TV 영상 URL 첨부 시 사용자 웹사이트(en.sedaily.ai)에서 기사 하단에 자동재생되는 기능 추가.

### Changes

#### 1. Backend (3 files)
- ✅ `cms_update_handler.py`: Added 'naver_tv_url' to updatable fields (7개 필드)
- ✅ `article_handler.py`: Added naver_tv_url to ArticleDetailResponse and JSON response
- ✅ `dynamodb_client.py`: Added naver_tv_url to save_article (14개 필드)

#### 2. CMS Frontend (1 file)
- ✅ `cms/src/app/edit/page.tsx`: Added URL input field with placeholder
- ✅ Form state includes naver_tv_url
- ✅ Save operation includes naver_tv_url

#### 3. User Frontend (2 files)
- ✅ `frontend/src/app/article/page.tsx`: Added video player with autoplay
- ✅ URL conversion: /v/12345 → /embed/12345?autoPlay=true
- ✅ Responsive iframe (16:9 aspect ratio)
- ✅ `frontend/src/types/article.ts`: Added naver_tv_url to ArticleDetail interface

### Technical Details

**DynamoDB Schema**:
```python
# 13개 필드 → 14개 필드
'naver_tv_url': str  # NEW
```

**Naver TV Embed**:
```typescript
// URL 변환
const videoId = url.match(/\/v\/(\d+)/)?.[1];
const embedUrl = `https://tv.naver.com/embed/${videoId}?autoPlay=true`;
```

**Video Player**:
- 16:9 aspect ratio (responsive)
- Autoplay enabled
- Fullscreen support
- Positioned below article content

### Results
- ✅ CMS: 7개 편집 가능 필드 (naver_tv_url 추가)
- ✅ DynamoDB: 14개 필드 저장
- ✅ Frontend: 영상 자동재생
- ✅ Cost: $0 추가 비용
- ✅ Performance: 영향 없음

### Files Modified
1. `backend/handlers/cms_update_handler.py`
2. `backend/handlers/article_handler.py`
3. `backend/clients/dynamodb_client.py`
4. `cms/src/app/edit/page.tsx`
5. `frontend/src/app/article/page.tsx`
6. `frontend/src/types/article.ts`

### Deployment Status
- ⏳ Backend: Ready for deployment
- ⏳ CMS: Ready for build
- ⏳ Frontend: Ready for build

### Usage
1. **CMS Admin**: Edit article → Enter Naver TV URL → Save
2. **User**: Visit article → Scroll down → Video autoplays

---

## Phase 25: Complete Korean Removal from Frontend - COMPLETED (2025-12-10)

### Overview
프론트엔드(en.sedaily.ai)에서 한국어 완전 제거 - 카테고리 및 기자명 영문 변환.

### Changes
1. ✅ **카테고리 영문 변환**: 경제→finance, IT_과학→technology 등
2. ✅ **기자명 영문 추출**: Claude [BYLINE] 섹션에서 추출
3. ✅ **DynamoDB 저장**: 영문 카테고리 + 영문 기자명

### Results
- ✅ 프론트엔드 100% 영문 달성
- ✅ API 응답 한국어 제거
- ✅ 신규 기사부터 자동 적용

---

(이전 Phase들은 생략...)
