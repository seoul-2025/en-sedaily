# 2025-12-18: Complete Localization & UX Improvements (Phase 26)

## Objectives
- Eliminate all remaining Korean text from the English frontend
- Implement automatic Korean-to-English name romanization for reporters
- Improve image handling and fallback behavior
- Enhance search page UX with loading animations
- Add social media links to footer

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `src/constants/categories.ts` | Modified | Extended category mapping (15+ categories) |
| `src/constants/reporterNames.ts` | Created | Korean reporter name → English mapping table |
| `src/types/article.ts` | Modified | Added new category types (regional, industry, realestate) |
| `src/types/aromanize.d.ts` | Created | TypeScript declarations for aromanize library |
| `src/utils/categoryUtils.ts` | Created | Shared category translation utility |
| `src/utils/convertByline.ts` | Created | Byline romanization with mapping + aromanize fallback |
| `src/app/article/page.tsx` | Modified | English categories, bylines, metadata, hashtag filtering |
| `src/app/search/page.tsx` | Modified | English categories, wave loader, image fallback |
| `src/app/page.tsx` | Modified | Prioritize articles with images for featured section |
| `src/app/[category]/CategoryClient.tsx` | Modified | Hero image fallback, prioritize articles with images |
| `src/components/home/HeroSection/HeroSection.tsx` | Modified | Image error fallback with logo placeholder |
| `src/components/common/Footer/Footer.tsx` | Modified | Added social media links |
| `src/components/home/Newsletter/Newsletter.tsx` | Modified | Fixed button text visibility |
| `src/components/article/ArticleImage.tsx` | Modified | Removed "Image not available" text |
| `src/app/opengraph-image.tsx` | Renamed | → `.bak` to use static OG image for social previews |
| `package.json` | Modified | Added aromanize dependency |

## Key Changes

### 1. Extended Category Mapping

**Added categories:**
```typescript
// src/constants/categories.ts
export const CATEGORY_MAP: Record<string, Category> = {
  // Basic categories
  정치: "politics",
  경제: "finance",
  국제: "international",
  문화: "culture",
  IT_과학: "technology",
  스포츠: "sports",
  사회: "society",

  // Extended categories
  지역: "regional",
  산업: "industry",
  부동산: "realestate",
  증권: "finance",
  금융: "finance",
  기업: "industry",
  생활: "society",
  연예: "culture",
  오피니언: "society",
  // ...
};
```

### 2. Byline Romanization System

**New utility:** `src/utils/convertByline.ts`

Features:
- Mapping table lookup (40+ reporter names)
- Automatic romanization via `aromanize` library
- Western name order: "Given-name Surname" (e.g., "Tae-gyu Lee")
- Graceful fallback to "Seoul Economic Daily"

```typescript
// Example conversions:
"워싱턴=이태규 특파원" → "By Tae-gyu Lee"
"김윤수 기자" → "By Yoon-su Kim"
```

### 3. Search Page Improvements

**Wave Loader Animation:**
```tsx
function WaveLoader() {
  return (
    <div className="flex items-center gap-2">
      {[0, 1, 2, 3, 4].map((i) => (
        <span
          key={i}
          className="w-3 h-3 bg-[var(--color-accent)] rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.1}s` }}
        />
      ))}
    </div>
  );
}
```

**Category Translation:**
```tsx
<span>{getCategoryInEnglish(article.category || 'business')}</span>
```

### 4. Hashtag Filtering

**Filter invalid tags like `#**`:**
```typescript
.filter((tag: string) => {
  const cleaned = tag.trim().replace(/^#/, '');
  return cleaned &&
         cleaned.length > 0 &&
         !/^\*+$/.test(cleaned) &&
         /[a-zA-Z가-힣0-9]/.test(cleaned);
})
```

### 5. Image Fallback System

**Prioritize articles with images:**
```typescript
// Select first article with original_link as featured
const articleWithImage = articles.find((a) => a.original_link);
const featuredArticle = articleWithImage || articles[0];
```

**Logo placeholder on error:**
```tsx
function HeroImage({ src, alt }) {
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return (
      <div className="w-full h-64 bg-white flex items-center justify-center">
        <img src="/sedaily-og-image.png" alt="Seoul Economic Daily" />
      </div>
    );
  }
  // ...
}
```

### 6. Footer Social Links

**Added platforms:**
- YouTube
- Naver TV
- Instagram
- Naver Blog
- Facebook
- X (Twitter)

**Custom icons for X and Naver (not available in lucide-react)**

### 7. OpenGraph Image Fix

**Issue:** Dynamic `opengraph-image.tsx` was overriding static OG image for social media previews (KakaoTalk, etc.)

**Solution:** Renamed `opengraph-image.tsx` → `opengraph-image.tsx.bak` to use static `sedaily-og-image.png` defined in metadata.

### 8. Metadata Localization

All SEO metadata now in English:
- `<meta name="author">` → English name
- OpenGraph `og:author` → English name
- OpenGraph `og:section` → English category
- JSON-LD `author.name` → English name
- JSON-LD `articleSection` → English category

## Dependencies Added

```json
{
  "aromanize": "^1.0.2"
}
```

## Deployment Status
- [x] Local testing
- [x] Build verification
- [x] Deployed to production

## Related Documentation
- README.md updated with Phase 26 changelog
- Category mapping reference: `src/constants/categories.ts`
- Reporter name mapping: `src/constants/reporterNames.ts`

## Next Steps (Optional)
- Add more reporter names to mapping table as needed
- Consider backend solution for storing English bylines
- Monitor for any unmapped categories in production

---

*Deployed: 2025-12-18 21:45 KST*
*Phase: 26*
*Status: Complete*
