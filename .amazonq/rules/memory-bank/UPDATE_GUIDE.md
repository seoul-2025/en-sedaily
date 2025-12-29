# Memory Bank Auto-Update Guide

## 자동 업데이트 시스템

이 파일이 있으면 Amazon Q가 자동으로 메모리뱅크를 업데이트합니다.

---

## 업데이트 트리거

다음 상황에서 **자동으로** 메모리뱅크가 업데이트됩니다:

### 1. 코드 변경 감지
- Backend 파일 수정 (`backend/` 폴더)
- Frontend 파일 수정 (`frontend/` 폴더)
- Infrastructure 파일 수정 (`infrastructure/` 폴더)

### 2. 새로운 Phase 완료
- "Phase X 완료" 언급 시
- "배포 완료" 언급 시
- "버그 수정" 언급 시

### 3. 주요 기능 추가/변경
- 새로운 Lambda 함수
- 새로운 API 엔드포인트
- 새로운 프론트엔드 페이지
- 데이터베이스 스키마 변경

---

## 자동 업데이트 규칙

### 항상 업데이트 (Every Change)
1. **`recent-changes.md`**
   - 맨 위에 새 섹션 추가
   - 날짜, Phase 번호, 변경사항 포함
   - 최근 10개 Phase만 유지

2. **`new-project-direction.md`**
   - "Current Status" 섹션 업데이트
   - "Last Updated" 날짜 갱신
   - "Completed Work" 리스트 업데이트

### 조건부 업데이트 (Major Changes Only)
3. **`complete-codebase-analysis.md`**
   - 새로운 파일 추가 시
   - 주요 로직 변경 시
   - 아키텍처 변경 시

4. **`structure.md`**
   - 새로운 디렉토리 추가 시
   - 파일 구조 변경 시

5. **`tech.md`**
   - 새로운 라이브러리 추가 시
   - 버전 업그레이드 시

### 절대 업데이트 안 함 (Stable)
6. **`guidelines.md`** - 개발 가이드라인 (안정적)
7. **`product.md`** - 제품 개요 (안정적)
8. **`deployment-notes.md`** - 배포 프로세스 (안정적)

---

## 업데이트 포맷

### recent-changes.md 추가 형식
```markdown
## Phase X: [제목] - COMPLETED (YYYY-MM-DD)

### Overview
[간단한 설명]

### Changes
1. ✅ [변경사항 1]
2. ✅ [변경사항 2]
3. ✅ [변경사항 3]

### Files Modified
- `path/to/file1.py`
- `path/to/file2.tsx`

### Results
- ✅ [결과 1]
- ✅ [결과 2]

---
```

### new-project-direction.md 업데이트 형식
```markdown
**Status**: ✅ Phase X Complete
**Last Updated**: YYYY-MM-DD (Phase X: [제목])
**Latest Updates (Phase X - YYYY-MM-DD)**:
- ✅ [변경사항 1]
- ✅ [변경사항 2]
```

---

## 사용자 명령어

### 자동 업데이트 (추천)
```
"Phase 16 완료했어"
"Lambda 타임아웃 늘렸어"
"버그 수정했어"
```
→ Amazon Q가 자동으로 관련 파일 업데이트

### 수동 업데이트
```
"recent-changes.md만 업데이트해줘"
"메모리뱅크 전체 업데이트해줘"
```

### 확인
```
"메모리뱅크 상태 확인해줘"
"최근 업데이트 내역 보여줘"
```

---

## 업데이트 우선순위

### High Priority (즉시 업데이트)
- Phase 완료
- 프로덕션 배포
- 중요 버그 수정
- 아키텍처 변경

### Medium Priority (다음 세션)
- 코드 리팩토링
- 성능 최적화
- UI/UX 개선

### Low Priority (주기적)
- 문서 정리
- 주석 추가
- 코드 스타일 변경

---

## 자동 정리 규칙

### recent-changes.md
- 최근 10개 Phase만 유지
- 오래된 Phase는 자동 삭제
- 중요한 Phase는 "Key Milestones" 섹션으로 이동

### complete-codebase-analysis.md
- 삭제된 파일 정보 제거
- 변경된 코드 스니펫 업데이트
- 최신 성능 지표 반영

---

## 백업 정책

### 자동 백업
- 메모리뱅크 업데이트 전 자동 백업
- 백업 위치: `.amazonq/rules/memory-bank/.backup/`
- 최근 5개 버전 유지

### 복구
```
"메모리뱅크 이전 버전으로 복구해줘"
"백업 목록 보여줘"
```

---

## 예시 시나리오

### 시나리오 1: 새로운 기능 추가
**사용자:** "Phase 16 완료했어. 이미지 업로드 기능 추가했어"

**자동 업데이트:**
1. `recent-changes.md` - Phase 16 섹션 추가
2. `new-project-direction.md` - Current Status 업데이트
3. `complete-codebase-analysis.md` - 새 파일 정보 추가

### 시나리오 2: 버그 수정
**사용자:** "DynamoDB 연결 에러 수정했어"

**자동 업데이트:**
1. `recent-changes.md` - 버그 수정 섹션 추가
2. `new-project-direction.md` - Last Updated 갱신

### 시나리오 3: 대규모 리팩토링
**사용자:** "백엔드 전체 리팩토링 완료"

**자동 업데이트:**
1. `recent-changes.md` - 리팩토링 섹션 추가
2. `new-project-direction.md` - Current Status 업데이트
3. `complete-codebase-analysis.md` - 전체 코드 분석 갱신
4. `structure.md` - 구조 변경 반영

---

## 비활성화

자동 업데이트를 원하지 않으면:
```
"자동 업데이트 비활성화해줘"
```

또는 이 파일을 삭제하세요:
```bash
rm .amazonq/rules/memory-bank/UPDATE_GUIDE.md
```

---

## 문제 해결

### 업데이트가 안 될 때
1. 이 파일이 존재하는지 확인
2. 명확한 변경사항 설명
3. "메모리뱅크 강제 업데이트해줘"

### 잘못된 업데이트
```
"메모리뱅크 이전 버전으로 복구해줘"
```

---

**Last Updated**: 2025-01-08
**Version**: 1.0
**Status**: ✅ Active
