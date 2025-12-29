# Google 검색 노출 가이드

**목표**: en.sedaily.ai 기사들이 구글 검색 및 AI 검색에 노출되도록 설정

## ✅ 완료된 작업

### 1. 동적 Sitemap 생성 (2025-01-08)
- **파일**: `frontend/src/app/sitemap.ts`
- **내용**: 2,916개 기사 포함
- **URL**: https://en.sedaily.ai/sitemap.xml
- **배포**: 2025-12-08 완료

### 2. Google Search Console 인증 (2025-12-08)
- ✅ 인증 파일: `google7727df7e42139b6d.html` 업로드 완료
- ✅ URL: https://en.sedaily.ai/google7727df7e42139b6d.html
- ✅ 소유권 인증 준비 완료

### 3. 기본 SEO 설정
- ✅ robots.txt: 크롤링 허용
- ✅ Sitemap: 2,916개 기사
- ✅ JSON-LD 구조화 데이터
- ✅ Meta 태그 (title, description)
- ✅ Open Graph 태그

## 🚀 다음 단계 (Google Search Console)

### 1단계: 소유권 인증 확인

1. https://search.google.com/search-console 접속
2. 속성: en.sedaily.ai 선택
3. "확인" 버튼 클릭
4. ✅ 인증 완료

**예상 시간**: 1분

### 2단계: Sitemap 제출

1. https://search.google.com/search-console 접속
2. 속성: en.sedaily.ai 선택
3. 좌측 메뉴 → "Sitemaps"
4. 새 사이트맵 추가: `https://en.sedaily.ai/sitemap.xml`
5. "제출" 클릭

**예상 시간**: 2분

### 3단계: 주요 기사 수동 색인 요청 (빠른 노출)

빠른 노출을 위해 주요 기사 10-20개 수동 요청:

1. Google Search Console → "URL 검사"
2. 기사 URL 입력 (예: `https://en.sedaily.ai/article?id=02100311.20251204170230001`)
3. "색인 생성 요청" 클릭
4. 10-20개 반복

**예상 시간**: 10분

## 📊 검색 노출 예상 시간

| 방법 | 예상 시간 |
|------|----------|
| Sitemap 제출 | 1-7일 |
| 수동 색인 요청 | 1-3일 |
| 자연 크롤링 | 1-4주 |

## 🔍 노출 확인 방법

### Google 검색
```
site:en.sedaily.ai
```

### 특정 기사 확인
```
site:en.sedaily.ai "기사 제목"
```

### Google Search Console
- "실적" 탭에서 노출수, 클릭수 확인
- "색인 생성" 탭에서 색인된 페이지 수 확인

## 🤖 AI 검색 엔진 노출

### Perplexity
- Google 색인 후 자동 반영
- 예상 시간: Google 색인 + 1-2주

### ChatGPT Search
- Google 색인 후 자동 반영
- 예상 시간: Google 색인 + 1-2주

### Claude
- 웹 검색 기능 사용 시 자동 반영
- 예상 시간: Google 색인 + 1-2주

## 📈 SEO 개선 사항 (이미 완료)

### 구조화 데이터 (JSON-LD)
- ✅ WebSite schema (홈페이지)
- ✅ NewsArticle schema (기사 페이지)
- ✅ ItemList schema (카테고리 페이지)

### 메타데이터
- ✅ title, description (각 페이지)
- ✅ keywords, hashtags (기사 페이지)
- ✅ Open Graph (소셜 미디어)
- ✅ Twitter Card

### 기술적 SEO
- ✅ HTTPS (SSL 인증서)
- ✅ 모바일 반응형
- ✅ 빠른 로딩 속도 (97.1kB First Load JS)
- ✅ 정적 사이트 생성 (SSG)

## 🎯 다음 단계 (선택)

### 1. 기사 페이지 Server-Side 렌더링
현재 기사 페이지는 Client-side 렌더링입니다.
Server-side로 변경하면 SEO가 더 개선됩니다.

**우선순위**: 중간 (현재도 JSON-LD로 충분)

### 2. 백링크 구축
- 서울경제 메인 사이트에서 링크
- 소셜 미디어 공유
- 뉴스 애그리게이터 등록

**우선순위**: 낮음 (자연스럽게 증가)

### 3. 콘텐츠 최적화
- 기사 제목 SEO 최적화
- Meta description 개선
- 내부 링크 추가

**우선순위**: 낮음 (자동 번역으로 충분)

## 📞 문제 해결

### Sitemap이 보이지 않음
```bash
# CloudFront 캐시 무효화
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/sitemap.xml"
```

### 기사가 색인되지 않음
1. robots.txt 확인: https://en.sedaily.ai/robots.txt
2. Google Search Console → "URL 검사"
3. 색인 생성 차단 여부 확인

### 검색 결과에 나타나지 않음
- 인내심 필요 (1-7일)
- Google Search Console에서 진행 상황 확인
- 수동 색인 요청 반복

## 📝 체크리스트

배포 후 확인:
- [ ] 프론트엔드 재빌드 완료
- [ ] S3 업로드 완료
- [ ] CloudFront 무효화 완료
- [ ] Sitemap 접근 가능 (https://en.sedaily.ai/sitemap.xml)
- [ ] Google Search Console에 Sitemap 제출
- [ ] 주요 기사 10개 수동 색인 요청
- [ ] 1주일 후 `site:en.sedaily.ai` 검색 확인

## 🎉 예상 결과

**1주일 후**:
- Google 검색에 기사 노출 시작
- Search Console에 노출수 데이터 표시

**2주일 후**:
- 대부분의 기사 색인 완료
- AI 검색 엔진에서 발견 가능

**1개월 후**:
- 안정적인 검색 트래픽
- 자동 크롤링으로 신규 기사 색인
