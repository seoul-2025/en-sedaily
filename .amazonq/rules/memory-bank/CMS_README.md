# CMS (Content Management System)

**Last Updated**: 2025-01-08 (Phase 16)

## ✅ 배포 완료

### Backend (DEPLOYED)
- **Lambda Functions**: 5개 배포 완료
- **API Gateway**: 엔드포인트 5개 추가 완료
- **Infrastructure**: S3 + CloudFront 생성 완료

### Frontend (DEPLOYED)
- **Status**: S3 + CloudFront 배포 완료
- **Custom Domain**: enadmin.sedaily.ai
- **SSL**: Wildcard certificate (*.sedaily.ai)

## 🚀 접속

**CMS URL**: https://enadmin.sedaily.ai

**로컬 개발** (선택사항):
```bash
cd cms
npm install
npm run dev
```
→ http://localhost:3001

## 📊 API 엔드포인트

**Base URL**: https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev

- `GET /admin/articles` - 기사 목록
- `GET /admin/articles/{id}` - 기사 상세
- `PUT /admin/articles/{id}` - 기사 수정
- `DELETE /admin/articles/{id}` - 기사 삭제
- `POST /admin/articles/bulk` - 대량 수정

## 💰 비용

- **추가 비용**: ~$5/월 (Lambda 5개)
- **총 비용**: $71 → $76/월

## 📝 향후 개선

1. ✅ S3 + CloudFront 배포 - 완료
2. ✅ 커스텀 도메인 (enadmin.sedaily.ai) - 완료
3. AWS Cognito 인증

상세 내용: `.amazonq/rules/memory-bank/CMS_DEPLOYMENT_STATUS.md`
