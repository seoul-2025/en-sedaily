# 배포 로그 - Google 검색 노출 최적화

**날짜**: 2025-01-08
**목적**: en.sedaily.ai 기사들이 구글 검색 및 AI 검색에 노출되도록 설정

## ✅ 완료된 작업

### 1. 동적 Sitemap 생성 (13:24 KST)
- **파일**: `frontend/src/app/sitemap.ts`
- **변경사항**: 정적 sitemap → 동적 sitemap (최신 기사 100개 포함)
- **결과**: 총 109개 URL (카테고리 9개 + 기사 100개)

### 2. 프론트엔드 빌드 (13:24 KST)
```bash
cd frontend
rm -rf .next out
npm run build
```
- **빌드 시간**: ~30초
- **First Load JS**: 97.1 kB (변경 없음)
- **Static Pages**: 15개 생성

### 3. S3 업로드 (13:24 KST)
```bash
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
```
- **업로드 파일**: 56개
- **삭제 파일**: 3개 (구버전)
- **총 크기**: 1.4 MB

### 4. CloudFront 캐시 무효화 (13:24 KST)
```bash
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```
- **Invalidation ID**: I3ZDAF36HUIQTJN1S4IB21J5PW
- **Status**: InProgress
- **예상 완료**: 1-2분

### 5. Sitemap 검증 (13:25 KST)
```bash
curl https://en.sedaily.ai/sitemap.xml
```
- **총 URL**: 109개
- **카테고리 페이지**: 9개
- **기사 페이지**: 100개
- **형식**: XML (정상)

## 📊 Sitemap 구조

### 정적 페이지 (9개)
1. https://en.sedaily.ai (priority: 1.0)
2. https://en.sedaily.ai/finance (priority: 0.9)
3. https://en.sedaily.ai/technology (priority: 0.9)
4. https://en.sedaily.ai/politics (priority: 0.9)
5. https://en.sedaily.ai/society (priority: 0.8)
6. https://en.sedaily.ai/culture (priority: 0.8)
7. https://en.sedaily.ai/sports (priority: 0.8)
8. https://en.sedaily.ai/international (priority: 0.8)
9. https://en.sedaily.ai/search (priority: 0.5)

### 동적 기사 페이지 (100개)
- **형식**: `https://en.sedaily.ai/article?id={news_id}`
- **Priority**: 0.7
- **Change Frequency**: weekly
- **Last Modified**: 각 기사의 published_at 날짜

## 🚀 다음 단계 (수동 작업 필요)

### 1. Google Search Console - Sitemap 제출 (필수)

**URL**: https://search.google.com/search-console

**단계**:
1. 속성 선택: en.sedaily.ai
2. 좌측 메뉴 → "Sitemaps"
3. 새 사이트맵 추가: `https://en.sedaily.ai/sitemap.xml`
4. "제출" 클릭

**예상 시간**: 2분

### 2. 주요 기사 수동 색인 요청 (선택, 빠른 노출)

**URL**: https://search.google.com/search-console

**단계**:
1. "URL 검사" 도구 선택
2. 기사 URL 입력 (예: `https://en.sedaily.ai/article?id=02100311.20251204170230001`)
3. "색인 생성 요청" 클릭
4. 10-20개 주요 기사 반복

**예상 시간**: 10분

### 3. 노출 확인 (1주일 후)

**Google 검색**:
```
site:en.sedaily.ai
```

**특정 기사 검색**:
```
site:en.sedaily.ai "Samsung"
site:en.sedaily.ai "Korea"
```

## ⏱️ 예상 타임라인

| 단계 | 예상 시간 |
|------|----------|
| Sitemap 제출 | 즉시 |
| Google 크롤링 시작 | 1-3일 |
| 기사 색인 완료 | 3-7일 |
| 검색 결과 노출 | 1-2주 |
| AI 검색 엔진 반영 | 2-4주 |

## 📈 모니터링 방법

### Google Search Console
1. **실적** 탭
   - 노출수 (Impressions)
   - 클릭수 (Clicks)
   - 평균 게재순위

2. **색인 생성** 탭
   - 색인된 페이지 수
   - 색인 생성 오류

3. **Sitemaps** 탭
   - 제출된 URL 수
   - 색인된 URL 수

### 수동 확인
```bash
# 전체 사이트 색인 확인
site:en.sedaily.ai

# 기사 페이지만 확인
site:en.sedaily.ai inurl:article

# 특정 키워드 확인
site:en.sedaily.ai "Samsung Electronics"
```

## 🎯 성공 지표

### 1주일 후
- [ ] Google Search Console에 노출수 데이터 표시
- [ ] `site:en.sedaily.ai` 검색 시 10개 이상 결과
- [ ] 주요 기사 색인 완료

### 2주일 후
- [ ] 100개 이상 페이지 색인
- [ ] 일일 노출수 100+ 
- [ ] 일일 클릭수 10+

### 1개월 후
- [ ] 안정적인 검색 트래픽
- [ ] AI 검색 엔진에서 발견 가능
- [ ] 자동 크롤링으로 신규 기사 색인

## 🔧 기술 세부사항

### Sitemap 생성 로직
```typescript
// frontend/src/app/sitemap.ts
async function getLatestArticles() {
    // API에서 최근 30일 기사 100개 가져오기
    const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        body: JSON.stringify({
            query: '*',
            filters: {
                published_from: (30일 전),
                published_until: (오늘),
            },
            page: 1,
            page_size: 100,
        }),
    });
    return data.articles || [];
}
```

### 빌드 시 자동 생성
- Next.js 빌드 시 sitemap.ts 실행
- API 호출하여 최신 기사 목록 가져오기
- XML 형식으로 sitemap.xml 생성
- S3에 업로드

### 업데이트 주기
- 프론트엔드 재빌드 시마다 자동 업데이트
- 현재: 수동 배포 시
- 권장: 일일 1회 자동 빌드 (선택사항)

## 📝 참고 문서

- **가이드**: `GOOGLE_INDEXING_GUIDE.md`
- **Sitemap 코드**: `frontend/src/app/sitemap.ts`
- **Robots.txt**: `frontend/src/app/robots.ts`

## ✅ 체크리스트

배포 완료:
- [x] 동적 Sitemap 코드 작성
- [x] 프론트엔드 빌드
- [x] S3 업로드
- [x] CloudFront 캐시 무효화
- [x] Sitemap 접근 확인 (https://en.sedaily.ai/sitemap.xml)
- [x] 기사 URL 100개 포함 확인

수동 작업 필요:
- [ ] Google Search Console에 Sitemap 제출
- [ ] 주요 기사 10-20개 수동 색인 요청
- [ ] 1주일 후 노출 확인

## 🎉 결과

**배포 성공!**

- ✅ Sitemap 생성 완료 (109개 URL)
- ✅ 프론트엔드 배포 완료
- ✅ CloudFront 캐시 무효화 완료
- ✅ 즉시 접근 가능: https://en.sedaily.ai/sitemap.xml

**다음 단계**: Google Search Console에서 Sitemap 제출 (2분 소요)
