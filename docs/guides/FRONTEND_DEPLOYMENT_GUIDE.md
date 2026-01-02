# 프론트엔드 수동 배포 가이드

## 배포 준비 완료 ✅

**빌드 완료**: `deploy-20251223-104752.tar.gz` (생성 완료)
**EC2 서버**: 52.21.195.0
**배포 경로**: `/home/ec2-user/en-sedaily` 또는 `/home/ubuntu/en-sedaily`

---

## 방법 1: 간단한 rsync 배포 (권장)

### 1단계: 빌드 파일 확인
```bash
cd /Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/frontend
ls -la .next/standalone/
```

### 2단계: rsync로 파일 전송
```bash
# SSH 키 권한 설정
chmod 400 ~/.ssh/sedaily-ec2-key.pem

# EC2에 파일 동기화 (ubuntu 사용자인 경우)
rsync -avz --delete \
  -e "ssh -i ~/.ssh/sedaily-ec2-key.pem -o StrictHostKeyChecking=no" \
  .next/standalone/ \
  ubuntu@52.21.195.0:~/en-sedaily/

# 또는 ec2-user인 경우
rsync -avz --delete \
  -e "ssh -i ~/.ssh/sedaily-ec2-key.pem -o StrictHostKeyChecking=no" \
  .next/standalone/ \
  ec2-user@52.21.195.0:~/en-sedaily/

# static 파일도 복사
rsync -avz \
  -e "ssh -i ~/.ssh/sedaily-ec2-key.pem -o StrictHostKeyChecking=no" \
  .next/static/ \
  ubuntu@52.21.195.0:~/en-sedaily/.next/static/

# public 파일도 복사
rsync -avz \
  -e "ssh -i ~/.ssh/sedaily-ec2-key.pem -o StrictHostKeyChecking=no" \
  public/ \
  ubuntu@52.21.195.0:~/en-sedaily/public/
```

### 3단계: SSH로 EC2 접속 및 PM2 재시작
```bash
# EC2 접속
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0
# 또는
ssh -i ~/.ssh/sedaily-ec2-key.pem ec2-user@52.21.195.0

# 애플리케이션 디렉토리로 이동
cd ~/en-sedaily

# PM2 재시작
pm2 restart all
# 또는 특정 앱만 재시작
pm2 restart sedaily-eng

# 상태 확인
pm2 status
pm2 logs --lines 50
```

---

## 방법 2: 배포 패키지 사용

### 1단계: 배포 패키지 업로드
```bash
# 배포 패키지를 EC2로 전송
scp -i ~/.ssh/sedaily-ec2-key.pem \
  deploy-20251223-104752.tar.gz \
  ubuntu@52.21.195.0:~/

# 또는
scp -i ~/.ssh/sedaily-ec2-key.pem \
  deploy-20251223-104752.tar.gz \
  ec2-user@52.21.195.0:~/
```

### 2단계: EC2에서 배포 실행
```bash
# EC2 접속
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0

# PM2 중지
pm2 stop all

# 기존 디렉토리 백업 (선택사항)
mv ~/en-sedaily ~/en-sedaily-backup-$(date +%Y%m%d)

# 새 디렉토리 생성
mkdir -p ~/en-sedaily
cd ~/en-sedaily

# 배포 패키지 압축 해제
tar -xzf ~/deploy-20251223-104752.tar.gz

# PM2 시작
pm2 start ecosystem.config.js

# 상태 확인
pm2 status
pm2 logs --lines 20
```

---

## 방법 3: Git Pull 배포

### EC2에서 직접 실행
```bash
# EC2 접속
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0

# 프로젝트 디렉토리로 이동
cd ~/en-sedaily-1st-main/frontend

# 최신 코드 가져오기
git pull origin main

# 의존성 설치
npm install

# 빌드
npm run build

# PM2 재시작
pm2 restart all
```

---

## 문제 해결

### 1. SSH 연결 실패
```bash
# SSH 키 권한 확인
chmod 400 ~/.ssh/sedaily-ec2-key.pem

# EC2 보안 그룹 확인
# - 포트 22 (SSH) 허용 확인
# - 현재 IP 주소 허용 확인

# 연결 테스트
ssh -i ~/.ssh/sedaily-ec2-key.pem -v ubuntu@52.21.195.0
```

### 2. PM2 상태 확인
```bash
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0 "pm2 status"
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0 "pm2 logs --lines 50"
```

### 3. 빌드 파일 누락
```bash
# 로컬에서 다시 빌드
cd /Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/frontend
npm run build

# standalone 디렉토리 확인
ls -la .next/standalone/
```

---

## 배포 후 검증

### 1. 웹사이트 접근 확인
```bash
# 직접 EC2 접근 (포트 3000)
curl http://52.21.195.0:3000

# 프로덕션 도메인
curl https://en.sedaily.com
```

### 2. SEO URL 테스트
```bash
# 새 URL 형식 테스트
curl -I https://en.sedaily.com/news/2025/12/22/cambodias-top-university-delegation-visits-busan-to-launch

# 레거시 URL 리다이렉트 테스트
curl -I https://en.sedaily.com/article?id=02100311.20251222103805001
```

### 3. Sitemap 확인
```bash
curl https://en.sedaily.com/sitemap.xml | head -100
```

---

## 빠른 배포 (추천)

가장 빠르고 간단한 방법:

```bash
# 1. 빌드가 이미 완료되었으므로 rsync만 실행
cd /Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/frontend

# 2. 파일 전송 (ubuntu 사용자 가정)
rsync -avz --delete -e "ssh -i ~/.ssh/sedaily-ec2-key.pem" .next/standalone/ ubuntu@52.21.195.0:~/en-sedaily/
rsync -avz -e "ssh -i ~/.ssh/sedaily-ec2-key.pem" .next/static/ ubuntu@52.21.195.0:~/en-sedaily/.next/static/
rsync -avz -e "ssh -i ~/.ssh/sedaily-ec2-key.pem" public/ ubuntu@52.21.195.0:~/en-sedaily/public/

# 3. PM2 재시작
ssh -i ~/.ssh/sedaily-ec2-key.pem ubuntu@52.21.195.0 "cd ~/en-sedaily && pm2 restart all && pm2 status"

# 4. 확인
curl -I https://en.sedaily.com
```

---

## 다음 단계

배포 완료 후:

1. ✅ **프로덕션 URL 테스트**
   ```bash
   curl -I https://en.sedaily.com/news/2025/12/22/cambodias-top-university-delegation-visits-busan-to-launch
   ```

2. ✅ **Google Search Console 업데이트**
   - https://search.google.com/search-console
   - 새 sitemap 제출: https://en.sedaily.com/sitemap.xml

3. ✅ **모니터링**
   - PM2 로그: `pm2 logs`
   - 에러 확인: `pm2 logs --err`
   - 성능 모니터링: `pm2 monit`
