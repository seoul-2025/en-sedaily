# Deployment Notes

## Critical: Frontend Deployment Process

### ⚠️ IMPORTANT: Always Full Rebuild for Frontend Changes

**프론트엔드 변경사항은 반드시 전체 재빌드 및 배포가 필요합니다.**

Next.js는 Static Site Generation (SSG)을 사용하므로, 코드 변경 후 반드시 전체 빌드를 해야 변경사항이 반영됩니다.

### Full Deployment Command

```bash
cd frontend
rm -rf .next out
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
```

### Why Full Rebuild is Required

1. **Static Site Generation**: Next.js는 빌드 타임에 모든 페이지를 HTML로 생성
2. **Build Cache**: `.next` 폴더에 캐시가 남아있으면 변경사항이 반영 안 됨
3. **CloudFront Cache**: CDN 캐시도 무효화해야 함

### Partial Deployment (NOT RECOMMENDED)

단일 파일만 업데이트하는 것은 권장하지 않습니다:
```bash
# ❌ 이렇게 하지 마세요
aws s3 cp out/search.html s3://...
```

이유:
- JavaScript 번들 파일명이 변경될 수 있음
- CSS 파일명이 변경될 수 있음
- 페이지 간 의존성 문제 발생 가능

### Deployment Checklist

프론트엔드 변경 후:
- [ ] `.next` 및 `out` 폴더 삭제
- [ ] `npm run build` 실행
- [ ] S3 전체 동기화 (`--delete` 옵션 사용)
- [ ] CloudFront 전체 무효화 (`/*` 경로)
- [ ] 1-2분 대기
- [ ] 브라우저 강력 새로고침 (Cmd+Shift+R / Ctrl+Shift+R)

### Backend Deployment

백엔드는 Lambda 함수이므로 다른 프로세스:

```bash
cd backend
bash build_lambda.sh
```

이 스크립트는 자동으로:
1. Docker로 Linux 호환 패키지 빌드
2. S3에 업로드
3. Lambda 함수 업데이트

### Quick Reference

**Frontend**: 전체 재빌드 필수
**Backend**: Lambda 패키지 빌드 및 업데이트
**Infrastructure**: Terraform apply

### Common Issues

**문제**: 변경사항이 웹사이트에 반영 안 됨
**해결**: 
1. 전체 재빌드 (`rm -rf .next out && npm run build`)
2. S3 전체 동기화
3. CloudFront 무효화
4. 브라우저 캐시 클리어

**문제**: 일부 페이지만 업데이트됨
**해결**: 전체 재빌드 필요 (부분 배포 금지)

**문제**: CloudFront에서 이전 버전 표시
**해결**: 무효화 완료 대기 (1-2분) 후 강력 새로고침
