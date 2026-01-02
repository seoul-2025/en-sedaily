# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Phase-based documentation system (42 phase documents)
- Comprehensive docs/ directory structure
- Documentation index (docs/README.md)

### Changed
- Restructured README.md (2977 lines → 197 lines, 93% reduction)
- Moved all sections to dedicated documentation files
- Slimmed frontend/README.md (341 lines → 315 lines)

### Fixed
- Documentation organization and discoverability

---

## [1.5.0] - 2025-12-31

### Added
- **K-Business Connections Game** (Phase 52)
  - NYT Connections-style puzzle game
  - 16 Korean companies grouped into 4 categories
  - Full-screen immersive experience
  - Real-time timer for competitive gameplay
  - Article links for each category
  - Share results functionality
  - Page transition animations

### Changed
- Professional AWS architecture diagram with VPC/network details (Phase 51)
- AWS architecture documentation and verification (Phase 50)

---

## [1.4.0] - 2025-12-31

### Added
- AI Summary feature implementation (Phase 49)
- ~~Video analytics tracking system (Phase 44)~~ - Removed same day, see archive

### Fixed
- Hashtag search bug (case sensitivity) (Phase 48)
- Category filtering bug (Phase 45)

### Security
- Lambda search optimization and security hardening (Phase 47)

### Operations
- Enterprise-grade infrastructure monitoring (Phase 46)

---

## [1.3.0] - 2025-12-30

### Added
- 10-category structure sync (Phase 43)
- CMS settings page for Naver TV URL management (Phase 40)

### Changed
- Economic category segmentation improvements (Phase 41)
- Sitemap.xml route handler re-implementation (Phase 39)
- RSS feeds and Naver TV URL updates (Phase 38)

### Security
- AWS Secrets Manager migration (Phase 42)
- Migrated hardcoded secrets to AWS Secrets Manager
- Improved credential management

---

## [1.2.0] - 2025-12-27

### Added
- Naver TV video autoplay feature (Phase 37)

### Fixed
- CMS auto-revalidation for real-time updates (Phase 36)
- CMS pagination and on-demand ISR revalidation (Phase 35)

---

## [1.1.0] - 2025-12-25

### Performance
- ISR performance optimization with speed boost (Phase 34)
- Advanced GEO optimization with semantic chunking (Phase 33)
- GEO/AEO optimization for AI search engines (Phase 32)

---

## [1.0.0] - 2025-12-23

### Major Release
- **SSR Migration & SEO Optimization** (Phase 27)
  - Migrated from static site to Server-Side Rendering
  - Enhanced SEO capabilities
  - Real-time content updates

### Added
- Category page real-time update fix (Phase 31)
- Homepage content and international SEO (Phase 30)
- Article timestamp and category unification (Phase 29)
- SEO-friendly URL migration (Phase 28)

---

## [0.9.0] - 2025-12-18

### Added
- Complete localization support (Phase 26)
- Comprehensive i18n implementation

---

## [0.8.0] - 2025-12-08

### Added
- All articles accessible feature (Phase 23)

---

## [0.7.0] - 2025-12-05

### Added
- CMS article editor (Phase 16)
- Full-featured content management system

---

## [0.6.0] - 2025-12-04

### Fixed
- BigKinds API fields fix (Phase 13)

---

## [0.5.0] - 2025-12-03

### Added
- Seoul Economic logo integration (Phase 12.2)

### Changed
- Frontend code quality improvements (Phase 12)

### Fixed
- Critical bug fixes (Phase 11)
- Collector logic fix (Phase 10.1)
- Provider link fix (Phase 12.1)

### Performance
- Performance optimization (Phase 10)

---

## [0.4.0] - 2025-12-02

### Changed
- Collection strategy update (Phase 9)

---

## [0.3.0] - 2025-12-01

### Added
- Premium dark theme (Phase 6)

### Changed
- Performance & UX improvements (Phase 7)
- 7-category structure (Phase 5)

### Operations
- Cost optimization ($86 → $14/month for Lambda) (Phase 8)
- Content quality improvements (Phase 6.2)
- Header UX enhancements (Phase 6.1)

---

## [0.2.0] - 2025-11-30

### Added
- Google Analytics 4 integration (Phase 17)
- Google AdSense integration preparation (Phase 18)
- Deployment script enhancement (Phase 19)

---

## [0.1.0] - 2025-11-29

### Added
- Real-time updates (Phase 4)
- Initial project setup (Phases 1-3)
- Next.js frontend with SSR
- AWS Lambda backend
- Anthropic Claude translation (Phase 14)
- DynamoDB data storage
- Automated hourly article collection

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.5.0 | 2025-12-31 | K-Business Connections Game, AWS diagrams |
| 1.4.0 | 2025-12-31 | AI Summary, Video analytics |
| 1.3.0 | 2025-12-30 | 10-category structure, Secrets Manager |
| 1.2.0 | 2025-12-27 | Naver TV, CMS improvements |
| 1.1.0 | 2025-12-25 | Performance optimizations (ISR, GEO) |
| 1.0.0 | 2025-12-23 | SSR Migration, SEO optimization |
| 0.9.0 | 2025-12-18 | Complete localization |
| 0.8.0 | 2025-12-08 | All articles accessible |
| 0.7.0 | 2025-12-05 | CMS article editor |
| 0.6.0 | 2025-12-04 | BigKinds API fixes |
| 0.5.0 | 2025-12-03 | Quality & bug fixes |
| 0.4.0 | 2025-12-02 | Collection strategy |
| 0.3.0 | 2025-12-01 | Dark theme, cost optimization |
| 0.2.0 | 2025-11-30 | Analytics integration |
| 0.1.0 | 2025-11-29 | Initial release |

---

## Notes

- **Phase Documentation**: Detailed information for each phase available in `docs/phases/`
- **Breaking Changes**: Major version changes (1.0.0) indicate breaking changes or significant architectural shifts
- **Unreleased**: Changes in current development but not yet released

---

**For detailed phase information, see:**
- [Development Phases Index](docs/phases/README.md)
- [Technical Documentation](docs/TECHNICAL.md)
- [Architecture](docs/ARCHITECTURE.md)
