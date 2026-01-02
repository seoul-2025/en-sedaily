# Phase 29: Article Timestamp & Category Unification

**Timeline:** 2025-12-23
**Status:** ✅ Completed

---

- **Problem**: Articles showed "13h ago" instead of actual time, categories not filtering correctly
- Fixed timestamp extraction from news_id (actual publish time vs midnight)
- Migrated 8,544 articles to use actual timestamps from news_id
- Fixed formatRelativeTime to parse full ISO timestamp (not date-only)
- Lambda timeout increased: 5min → 15min
- Translation service response validation added
- Category unification: All English categories → Korean (164 articles migrated)
- Category filtering fix: search_handler now matches Korean categories correctly
- Frontend cache optimization: Category pages 10min → 5min
- Files modified: date_utils.py (NEW), article_collector.py, translation_service.py, search_handler.py, formatDate.ts, api.ts
- Scripts added: migrate_timestamps.py, migrate_categories_to_korean.py
- Result: All 7 categories now display latest articles (<1 hour), accurate relative timestamps

---

**Related Documentation:**
- See `docs/work-logs/` for detailed daily development activities
- See other phases in `docs/phases/`
