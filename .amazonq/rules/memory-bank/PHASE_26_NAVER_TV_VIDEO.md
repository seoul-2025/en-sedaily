# Phase 26: Naver TV Video Integration - IN PROGRESS

**Date**: 2025-01-08
**Status**: ✅ COMPLETED
**Goal**: CMS에서 네이버 TV 영상 링크 첨부 → 사용자 웹사이트에서 자동재생

---

## Overview

CMS 관리자가 네이버 TV 영상 URL을 기사에 첨부하면, en.sedaily.ai에서 기사 하단에 영상이 자동재생되는 기능 추가.

---

## Implementation Plan

### Phase 1: Backend ✅ COMPLETED
- [x] `cms_update_handler.py` - naver_tv_url 필드 추가
- [x] `article_handler.py` - naver_tv_url 반환 추가
- [x] `dynamodb_client.py` - save_article에 naver_tv_url 추가

### Phase 2: CMS Frontend ✅ COMPLETED
- [x] `cms/src/app/edit/page.tsx` - URL 입력 필드 추가
- [x] Form state에 naver_tv_url 추가
- [x] 저장 시 naver_tv_url 포함

### Phase 3: User Frontend ✅ COMPLETED
- [x] `frontend/src/app/article/page.tsx` - 영상 플레이어 추가
- [x] URL 변환 함수 구현 (v/12345 → embed/12345?autoPlay=true)
- [x] 자동재생 iframe 추가
- [x] `frontend/src/types/article.ts` - naver_tv_url 타입 추가

### Phase 4: Deployment ✅ COMPLETED
- [x] Backend: `./build_lambda.sh` (34.3 MB, 2025-12-10 05:42 UTC)
- [x] CMS: Build + S3 upload + CloudFront invalidation (EAEB9I2CA0NDK)
- [x] Frontend: Build + S3 upload + CloudFront invalidation (EUWQ1K71CXJUH)

---

## Technical Details

### DynamoDB Schema Change
```python
# 기존 13개 필드 → 14개 필드
{
    'news_id': str,
    'title_en': str,
    'content_en': str,
    # ... 기존 필드들 ...
    'naver_tv_url': str,  # ✅ NEW
}
```

### Naver TV Embed URL Format
```
입력: https://tv.naver.com/v/12345678
출력: https://tv.naver.com/embed/12345678?autoPlay=true
```

---

## Progress Log

### 2025-01-08 - Started
- Created Phase 26 documentation
- Ready to implement backend changes

### 2025-01-08 - Backend Complete ✅
- Modified `cms_update_handler.py`: Added 'naver_tv_url' to updatable fields
- Modified `article_handler.py`: Added naver_tv_url to ArticleDetailResponse dataclass and JSON response
- Modified `dynamodb_client.py`: Added naver_tv_url to save_article item

### 2025-01-08 - CMS Frontend Complete ✅
- Modified `cms/src/app/edit/page.tsx`: Added naver_tv_url to form state
- Added URL input field with placeholder
- Included naver_tv_url in save updates

### 2025-01-08 - User Frontend Complete ✅
- Modified `frontend/src/app/article/page.tsx`: Added video player with autoplay
- Implemented URL conversion: /v/12345 → /embed/12345?autoPlay=true
- Added responsive iframe (16:9 aspect ratio)
- Modified `frontend/src/types/article.ts`: Added naver_tv_url to ArticleDetail interface

### 2025-12-10 - Deployment Complete ✅
- Backend Lambda: 34.3 MB package deployed (search, article, collector)
- CMS: Built and deployed to S3 + CloudFront invalidation
- Frontend: Built and deployed to S3 + CloudFront invalidation
- All systems operational with naver_tv_url support

---

## Files to Modify

### Backend (3 files)
1. `backend/handlers/cms_update_handler.py`
2. `backend/handlers/article_handler.py`
3. `backend/clients/dynamodb_client.py`

### CMS (1 file)
1. `cms/src/app/edit/page.tsx`

### Frontend (1 file)
1. `frontend/src/app/article/page.tsx`

---

## Cost Impact

- **Additional Cost**: $0 (1 DynamoDB field = free)
- **Performance Impact**: None (client-side iframe)

---

## Next Steps

1. ✅ Create Phase 26 documentation
2. ⏳ Modify backend handlers
3. ⏳ Modify CMS frontend
4. ⏳ Modify user frontend
5. ⏳ Deploy all changes
