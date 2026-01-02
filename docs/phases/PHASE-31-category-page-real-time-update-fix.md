# Phase 31: Category Page Real-Time Update Fix

**Timeline:** 2025-12-23
**Status:** ✅ Completed

---

- **Problem**: Category pages showed 2-3 hour old articles despite main page showing latest articles
- **Root Cause 1**: middleware.ts forced 10-minute cache on all category pages (added Dec 17 for performance)
- **Root Cause 2**: [category]/page.tsx used ISR with 10-minute revalidation instead of dynamic rendering
- **Investigation Process**:
  - Verified BigKinds API → Lambda → DynamoDB pipeline working correctly (400+ articles collected daily)
  - Confirmed DynamoDB has latest articles (18:00~21:26 timestamp)
  - Tested API endpoints returning correct data (200 OK)
  - Found main page using `force-dynamic` while category pages used `revalidate: 600`
  - Discovered middleware.ts overriding all cache settings with `max-age=600`
- **Solution**:
  - middleware.ts: Changed category pages from `max-age=600` → `no-cache, no-store, must-revalidate`
  - [category]/page.tsx: Removed `export const revalidate = 600`, added `export const dynamic = "force-dynamic"`
  - Reverted to feature branch behavior (no middleware caching for categories)
- **Comparison with Feature Branch** (`feature/domain-en.sedaily.com-add`):
  - Feature branch: No middleware.ts, no ISR → Real-time updates 
  - Current main: middleware.ts + ISR added Dec 17 → Stale content 
- Files modified: middleware.ts, [category]/page.tsx
- Deployment: CloudFront cache invalidated, EC2 server restarted
- Result: All 7 categories now show real-time articles (Technology: 52, Finance: 185, Politics: 42, Society: 77, Culture: 18, Sports: 7, International: 19)
- Verified: Latest articles from 18:00~21:26 KST now appear immediately on category pages

---

**Related Documentation:**
- See `docs/work-logs/` for detailed daily development activities
- See other phases in `docs/phases/`
