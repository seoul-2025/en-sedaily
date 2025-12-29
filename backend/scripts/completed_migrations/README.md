# Completed Migration Scripts

이 디렉토리에는 **개발 환경(dev)**에서 성공적으로 실행 완료된 마이그레이션 스크립트가 보관되어 있습니다.

## 📋 보관 목적

다음 상황에서 재사용하기 위해 보관:
- **프로덕션 환경** 마이그레이션 시
- **재해 복구** (Disaster Recovery)
- **신규 환경** 구축 시
- **개발 히스토리** 참조

---

## 📁 스크립트 목록

### 1. create_gsi.sh (4.1KB)
**실행일**: 2025-12-22
**목적**: DynamoDB Global Secondary Index 생성
**결과**: ✅ 성공
- GSI 이름: `slug-index`
- 상태: `ACTIVE`
- 용도: slug 기반 기사 조회

**재실행 시 주의사항**:
- GSI가 이미 존재하면 스킵됨
- 생성 시 10-30분 소요

---

### 2. migrate_slugs.py (11KB)
**실행일**: 2025-12-22
**목적**: 기존 기사에 SEO-friendly slug 추가
**결과**: ✅ 99.8% 성공 (8,670/8,691 articles)

**마이그레이션 통계**:
- 총 기사: 8,691개
- 성공: 8,670개 (99.8%)
- 실패: 21개 (0.2%) - NULL slug 이슈

**생성된 slug 예시**:
```
Before: /article?id=02100311.20251218135803001
After:  /finance/2025/12/18/hamyang-county-breaks-ground-on-36-hole-park-golf-course
```

**재실행 시 주의사항**:
- `--dry-run` 플래그로 먼저 테스트
- 중복 slug 자동 처리 (날짜 접미사 추가)

**사용법**:
```bash
# 테스트 실행
python3 migrate_slugs.py --dry-run

# 실제 마이그레이션
python3 migrate_slugs.py

# 프로덕션 환경
python3 migrate_slugs.py --table seodaily-eng-articles-prod
```

---

### 3. migrate_timestamps.py (6.4KB)
**실행일**: 2025-12-23
**목적**: 기사 발행 시간 수정 (00:00:00 → 실제 시간)
**결과**: ✅ 성공

**문제 상황**:
- 기존: 모든 기사가 자정(00:00:00) 시간으로 저장됨
- 증상: "13h ago" 대신 "5h ago"로 잘못 표시됨

**해결 방법**:
- news_id에서 실제 발행 시간 추출
  - 예: `02100311.20251223090937001` → `2025-12-23T09:09:37`
- published_at 필드 업데이트

**사용법**:
```bash
# 테스트 실행
python3 migrate_timestamps.py --dry-run

# 실제 마이그레이션
python3 migrate_timestamps.py
```

---

### 4. migrate_categories_to_korean.py (6.6KB)
**실행일**: 2025-12-23
**목적**: 카테고리를 영어에서 한글로 통일
**결과**: ✅ 성공 (164개 기사 업데이트)

**문제 상황**:
- 기존 기사: 한글 카테고리 (경제, IT_과학 등) - 8,632개
- 신규 기사: 영어 카테고리 (finance, technology 등) - 138개
- 증상: 카테고리 필터링 불일치

**카테고리 매핑**:
```
finance      → 경제
technology   → IT_과학
politics     → 정치
society      → 사회
culture      → 문화
sports       → 스포츠
international → 국제
```

**마이그레이션 결과**:
- 업데이트: 164개
- 이미 한글: 8,632개 (스킵)
- 실패: 0개

**사용법**:
```bash
# 테스트 실행
python3 migrate_categories_to_korean.py --dry-run

# 실제 마이그레이션
python3 migrate_categories_to_korean.py
```

---

## 🚀 프로덕션 환경 마이그레이션 시퀀스

프로덕션 환경에 동일한 마이그레이션을 적용할 때는 다음 순서로 실행:

```bash
# 1단계: GSI 생성 (30분 소요)
./create_gsi.sh
# 완료 확인: aws dynamodb describe-table --table-name seodaily-eng-articles-prod --query 'Table.GlobalSecondaryIndexes[?IndexName==`slug-index`].IndexStatus'

# 2단계: Slug 마이그레이션 (테스트 → 실행)
python3 migrate_slugs.py --table seodaily-eng-articles-prod --dry-run
python3 migrate_slugs.py --table seodaily-eng-articles-prod

# 3단계: 시간 마이그레이션
python3 migrate_timestamps.py --dry-run
python3 migrate_timestamps.py

# 4단계: 카테고리 통일
python3 migrate_categories_to_korean.py --dry-run
python3 migrate_categories_to_korean.py
```

**예상 소요 시간**: 1-2시간 (GSI 생성 시간 포함)

---

## 📊 환경별 실행 기록

| 환경 | GSI | Slugs | Timestamps | Categories | 날짜 |
|------|-----|-------|-----------|------------|------|
| **Dev** | ✅ | ✅ | ✅ | ✅ | 2025-12-22~23 |
| **Prod** | ⏳ | ⏳ | ⏳ | ⏳ | 미실행 |

---

## ⚠️ 주의사항

### 공통 주의사항
1. **백업 필수**: 마이그레이션 전 DynamoDB 백업 생성
2. **Dry-run 필수**: 실제 실행 전 `--dry-run`으로 테스트
3. **오프피크 시간**: 프로덕션은 새벽 시간대 실행 권장
4. **모니터링**: Lambda 로그와 DynamoDB 메트릭 확인

### 롤백 계획
문제 발생 시:
1. DynamoDB Point-in-Time Recovery 사용
2. Lambda 함수 이전 버전으로 롤백
3. 프론트엔드는 기존 URL 형식 유지 (폴백 지원)

---

## 📞 문의

문제 발생 시 참조:
- 마이그레이션 가이드: `docs/archive/MIGRATION_GUIDE.md`
- 완료 보고서: `docs/archive/MIGRATION_COMPLETE.md`
- 슬러그 생성 로직: `../utils/slug_generator.py`
- DynamoDB 클라이언트: `../clients/dynamodb_client.py`

---

**작성일**: 2025-12-23
**환경**: seodaily-eng-articles-dev (us-east-1)
**상태**: ✅ All migrations completed successfully
