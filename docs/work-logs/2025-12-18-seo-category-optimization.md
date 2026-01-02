# 2025-12-18: SEO 카테고리 페이지 최적화

## 작업 목표

- 카테고리 페이지 SEO/AI 검색 최적화
- en.sedaily.com을 대표 도메인으로 canonical 설정
- E-E-A-T 신호 강화

## 배경

서울경제 영문 뉴스 사이트(en.sedaily.com)의 SEO 정착 초기 단계로,
카테고리 페이지에 메타데이터가 없어 검색엔진/AI 최적화가 필요했음.

### 도메인 구조
- 대표 도메인: `https://en.sedaily.com`
- 백업 도메인: `https://en.sedaily.ai` (CNAME 연결)

### SEO 전략
- canonical 중심 전략 (301 리디렉션 미적용)
- 모든 canonical URL은 en.sedaily.com 기준

---

## 변경 파일

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `frontend/src/app/[category]/page.tsx` | 수정 | CATEGORY_CONFIG SEO 최적화 |
| `frontend/src/app/[category]/page.tsx` | 수정 | generateMetadata 함수 추가 |
| `frontend/src/app/[category]/page.tsx` | 수정 | JSON-LD 구조화 데이터 추가 |
| `frontend/src/app/search/layout.tsx` | **신규** | 검색 페이지 메타데이터 |

---

## 주요 변경 내용

### 1. CATEGORY_CONFIG SEO 최적화

**Before:**
```typescript
const CATEGORY_CONFIG = {
  finance: {
    title: "Finance & Business",
    description: "Economy, finance, industry, and business news",
    color: "from-green-500 to-green-600",
  },
  technology: {
    title: "Technology",
    description: "IT, science, innovation, and tech industry updates",
    color: "from-indigo-500 to-indigo-600",
  },
  // ... 비슷한 패턴
};
```

**After:**
```typescript
const CATEGORY_CONFIG = {
  finance: {
    title: "South Korea Finance & Markets",
    description: "Financial news from South Korea, covering markets, banking, investments, and economic policy.",
    color: "from-green-500 to-green-600",
  },
  technology: {
    title: "South Korea Technology & Innovation News",
    description: "Coverage of South Korea's technology sector, including AI, semiconductors, startups, and digital innovation.",
    color: "from-indigo-500 to-indigo-600",
  },
  politics: {
    title: "South Korea Politics & Government Policy",
    description: "Latest news and analysis on South Korea's politics, government policies, diplomacy, and regulatory changes.",
    color: "from-blue-500 to-blue-600",
  },
  society: {
    title: "South Korea Society & Public Affairs",
    description: "In-depth coverage of South Korean society, including demographics, labor, education, housing, and social issues.",
    color: "from-purple-500 to-purple-600",
  },
  culture: {
    title: "South Korea Culture & Creative Industries",
    description: "Coverage of South Korea's culture, content industry, and creative sectors, including film, music, and cultural policy.",
    color: "from-pink-500 to-pink-600",
  },
  sports: {
    title: "South Korea Sports & Global Competitions",
    description: "News and analysis on South Korean sports, athletes, and the sports industry in international competitions.",
    color: "from-red-500 to-red-600",
  },
  international: {
    title: "Korea in Global Affairs",
    description: "International news and analysis related to South Korea's role in global politics, trade, and diplomacy.",
    color: "from-orange-500 to-orange-600",
  },
};
```

**근거:**
- "South Korea" 키워드: 지역 타겟팅으로 검색 차별화
- 상세 description: 메타 설명으로 활용, CTR 향상
- AI Search Optimization: AI가 지역 뉴스 출처로 인식

---

### 2. generateMetadata 함수 추가

**추가된 코드:**
```typescript
import { Metadata } from "next";

export async function generateMetadata({ params }: CategoryPageProps): Promise<Metadata> {
  const { category } = params;
  const config = CATEGORY_CONFIG[category];

  return {
    title: `${config.title} - Seoul Economic Daily`,
    description: config.description,
    keywords: `South Korea news, ${category}, Korean ${category}, Seoul Economic Daily, Korea business news`,
    alternates: {
      canonical: `https://en.sedaily.com/${category}`,
    },
    openGraph: {
      title: `${config.title} - Seoul Economic Daily`,
      description: config.description,
      url: `https://en.sedaily.com/${category}`,
      siteName: "Seoul Economic Daily",
      locale: "en_US",
      type: "website",
      images: [{ url: "https://en.sedaily.com/sedaily-og-image.png", width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      title: `${config.title} - Seoul Economic Daily`,
      description: config.description,
      site: "@sedaily_com",
    },
    robots: {
      index: true,
      follow: true,
      googleBot: { index: true, follow: true, "max-image-preview": "large" },
    },
  };
}
```

**근거:**
- canonical: 중복 콘텐츠 방지, 대표 URL 명시 (Google SEO 가이드)
- OpenGraph: 소셜 미디어 공유 최적화
- Twitter Cards: 트위터 카드 노출
- robots: Googlebot 크롤링 허용

---

### 3. JSON-LD 구조화 데이터 추가

**추가된 코드:**
```typescript
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  name: `${config.title} - Seoul Economic Daily`,
  description: config.description,
  url: `https://en.sedaily.com/${category}`,
  inLanguage: "en-US",
  isPartOf: {
    "@type": "WebSite",
    name: "Seoul Economic Daily",
    url: "https://en.sedaily.com",
  },
  publisher: {
    "@type": "NewsMediaOrganization",
    name: "Seoul Economic Daily",
    url: "https://en.sedaily.com",
    logo: { "@type": "ImageObject", url: "https://en.sedaily.com/sedaily-logo.png" },
  },
  mainEntity: {
    "@type": "ItemList",
    name: config.title,
    description: config.description,
  },
};
```

**근거:**
- CollectionPage: 카테고리/목록 페이지에 적합한 스키마 (schema.org)
- NewsMediaOrganization: 뉴스 미디어 출처 신뢰도 신호 (E-E-A-T)
- AI가 구조화 데이터를 통해 페이지 성격 정확히 이해

---

### 4. search/layout.tsx 신규 생성

**생성된 파일:** `frontend/src/app/search/layout.tsx`

```typescript
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Search Articles - Seoul Economic Daily",
  description: "Search news articles from Seoul Economic Daily, South Korea's leading business and financial news source.",
  alternates: {
    canonical: "https://en.sedaily.com/search",
  },
  robots: {
    index: false,  // 검색 결과 페이지는 색인 제외
    follow: true,  // 내부 링크는 팔로우
  },
};
```

**근거:**
- noindex: 검색 결과 페이지는 중복 콘텐츠 방지를 위해 색인 제외 권장
- follow: 내부 링크 크롤링은 허용

---

## 근거/참고자료

| 출처 | 내용 |
|------|------|
| [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) | SEO 기본 원칙 |
| [Google E-E-A-T 가이드](https://developers.google.com/search/blog/2022/12/google-raters-guidelines-e-e-a-t) | 신뢰/전문성 평가 기준 |
| [AI Search Optimization (Wikipedia)](https://en.wikipedia.org/wiki/AI_Search_Optimization) | AI 검색 최적화 전략 |
| [Schema.org CollectionPage](https://schema.org/CollectionPage) | 구조화 데이터 스키마 |

---

## 배포 상태

- [x] 코드 작성 완료
- [x] 로컬 테스트
- [x] 빌드 확인
- [x] 배포 완료 (2025-12-18 10:32 UTC)
- [ ] Google Search Console 확인

### 배포 정보
- **서버**: 52.21.195.0 (EC2)
- **백업**: backup_20251218_103140
- **PM2 상태**: online
- **HTTP 응답**: 200 OK

---

## 추가 작업: E-E-A-T 정적 페이지 생성 (2025-12-18 19:37 KST)

### 5. About 페이지 신규 생성

**생성된 파일:** `frontend/src/app/about/page.tsx`

- sedaily.com 원본 회사 정보 기반
- 회사명: Seoul Economic Daily Co., Ltd. (서울경제신문)
- 설립: 1960년
- CEO: 손동영 (Son Dong-young)
- 주소: 트윈트리타워 B동 14-16층
- JSON-LD: AboutPage + NewsMediaOrganization

**SEO 메타데이터:**
- title: "About Us - Seoul Economic Daily"
- canonical: `https://en.sedaily.com/about`
- OpenGraph, Twitter Cards 포함

---

### 6. Contact 페이지 신규 생성

**생성된 파일:** `frontend/src/app/contact/page.tsx`

- 전화번호: +82-2-724-8600
- 이메일: webmaster@sedaily.com
- 주소 (영문/한글 병기)
- 부서별 연락처
- 소셜 미디어 링크 (YouTube, Facebook, Twitter, Instagram)
- JSON-LD: ContactPage

---

### 7. Terms 페이지 신규 생성

**생성된 파일:** `frontend/src/app/terms/page.tsx`

- 이용약관 10개 섹션
- 한국법 적용 명시 (Republic of Korea)
- 회사 정보 포함
- JSON-LD: WebPage

---

### 8. Privacy 페이지 신규 생성

**생성된 파일:** `frontend/src/app/privacy/page.tsx`

- 개인정보처리방침 15개 섹션
- GDPR 및 한국 개인정보보호법(PIPA) 준수
- 데이터 수집/사용/보관 정책
- 사용자 권리 명시
- JSON-LD: WebPage

---

## 2차 배포 정보 (2025-12-18 19:37 KST)

- **백업**: backup_20251218_193745
- **PM2 상태**: online
- **HTTP 응답**:
  - /about: 200 OK ✓
  - /contact: 200 OK ✓
  - /terms: 200 OK ✓
  - /privacy: 200 OK ✓

---

## 미완료 작업 (보류)

| 작업 | 상태 | 사유 |
|------|------|------|
| robots.ts에서 en.sedaily.ai sitemap 제거 | 보류 | 사용자 요청으로 나중에 진행 |

---

## 다음 작업 제안

1. **Google Search Console**: URL 검사로 새 페이지 색인 요청
2. **Rich Results Test**: JSON-LD 구조화 데이터 검증
3. **robots.ts 정리**: en.sedaily.ai sitemap 제거 (시기 결정 필요)
4. **Footer 링크 확인**: About/Contact/Terms/Privacy 링크 연결 확인

---

*작성: Claude Code | 날짜: 2025-12-18*
*업데이트: 2025-12-18 19:37 KST - E-E-A-T 페이지 추가*
