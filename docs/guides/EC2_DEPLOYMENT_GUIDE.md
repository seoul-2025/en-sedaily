# EC2 배포 가이드 - Seoul Economic Daily English

## 📋 목차

1. [EC2 인스턴스 생성](#1-ec2-인스턴스-생성)
2. [초기 서버 설정](#2-초기-서버-설정)
3. [애플리케이션 배포](#3-애플리케이션-배포)
4. [SSL 인증서 설정](#4-ssl-인증서-설정)
5. [도메인 연결](#5-도메인-연결)
6. [모니터링 및 관리](#6-모니터링-및-관리)
7. [문제 해결](#7-문제-해결)

---

## 1. EC2 인스턴스 생성

### AWS Console에서 EC2 생성

1. **EC2 대시보드** → "Launch Instance"
2. **설정값**:
   - **Name**: `sedaily-eng-production`
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: `t3.small` (2 vCPU, 2GB RAM)
   - **Key Pair**: 새로 생성 또는 기존 키 사용
   - **Network Settings**:
     - VPC: 기본 VPC
     - Subnet: Public Subnet
     - Auto-assign Public IP: Enable
   - **Security Group**:
     ```
     - SSH (22): Your IP only
     - HTTP (80): 0.0.0.0/0
     - HTTPS (443): 0.0.0.0/0
     - Custom TCP (3000): Your IP (임시, 테스트용)
     ```
   - **Storage**: 20GB gp3
   - **Tags**:
     ```
     Name: sedaily-eng-production
     Environment: production
     Project: sedaily-english
     ```

### Elastic IP 할당 (권장)

```bash
# AWS Console에서
EC2 → Elastic IPs → Allocate Elastic IP → Associate with instance
```

---

## 2. 초기 서버 설정

### SSH 접속

```bash
# 로컬에서
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 서버 설정 스크립트 실행

```bash
# EC2에서
curl -O https://raw.githubusercontent.com/sedaily/en-sedaily-1st/main/frontend/setup-ec2.sh
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### 수동 설정 (스크립트 대신)

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Node.js 20 설치
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# PM2 설치
sudo npm install -g pm2
pm2 startup

# Nginx 설치
sudo apt install -y nginx

# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# 디렉토리 생성
mkdir -p ~/en-sedaily ~/logs ~/backups
```

---

## 3. 애플리케이션 배포

### 첫 배포

#### 로컬에서 준비

```bash
# frontend 디렉토리에서
vi deploy-ec2.sh

# EC2_HOST를 실제 IP로 변경
EC2_HOST="54.123.456.789"  # 실제 EC2 IP 입력

# 배포 실행
./deploy-ec2.sh
```

#### 또는 EC2에서 직접

```bash
# EC2에서
cd ~/en-sedaily
git clone https://github.com/sedaily/en-sedaily-1st.git .
cd frontend

# 환경변수 설정
cat > .env << EOF
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_API_URL=https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
EOF

# 빌드
npm install
npm run build

# PM2로 시작
pm2 start ecosystem.config.js
pm2 save
```

### Nginx 설정

```bash
# nginx.conf 복사
sudo cp ~/en-sedaily/frontend/nginx.conf /etc/nginx/sites-available/sedaily-eng

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/sedaily-eng /etc/nginx/sites-enabled/

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 4. SSL 인증서 설정

### Let's Encrypt 인증서 발급

```bash
# 도메인이 EC2 IP를 가리키는지 확인
nslookup en.sedaily.com

# 인증서 발급
sudo certbot --nginx -d en.sedaily.com -d en.sedaily.ai

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

---

## 5. 도메인 연결

### Route 53 설정

```
1. Route 53 → Hosted Zones → sedaily.com
2. Create Record:
   - Name: en
   - Type: A
   - Value: EC2 Elastic IP
   - TTL: 300
```

### CloudFlare 설정 (대안)

```
1. DNS → Add Record
2. Type: A
3. Name: en
4. IPv4 address: EC2 IP
5. Proxy status: DNS only (처음에는)
```

---

## 6. 모니터링 및 관리

### PM2 모니터링

```bash
# 상태 확인
pm2 status
pm2 monit

# 로그 확인
pm2 logs sedaily-eng
pm2 logs sedaily-eng --lines 100

# 재시작
pm2 restart sedaily-eng
pm2 reload sedaily-eng  # Zero-downtime

# 메모리/CPU 확인
pm2 info sedaily-eng
```

### Nginx 로그

```bash
# Access logs
tail -f /var/log/nginx/sedaily-access.log

# Error logs
tail -f /var/log/nginx/sedaily-error.log
```

### 시스템 모니터링

```bash
# CPU/메모리
htop

# 디스크 사용량
df -h

# 네트워크 연결
netstat -tlpn

# PM2 웹 모니터링 (선택)
pm2 install pm2-server-monit
pm2 web
```

### CloudWatch 설정 (권장)

```bash
# CloudWatch Agent 설정
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# 메트릭 수집 시작
sudo systemctl start amazon-cloudwatch-agent
```

---

## 7. 문제 해결

### 일반적인 문제

#### 502 Bad Gateway

```bash
# PM2 프로세스 확인
pm2 status
pm2 restart sedaily-eng

# 포트 확인
sudo netstat -tlpn | grep 3000
```

#### 메모리 부족

```bash
# Swap 확인
free -h

# PM2 메모리 제한 조정
pm2 delete sedaily-eng
pm2 start ecosystem.config.js --max-memory-restart 1500M
```

#### 느린 응답

```bash
# PM2 인스턴스 수 조정
pm2 scale sedaily-eng 2  # 2개 인스턴스로

# Nginx 캐시 확인
sudo nginx -T | grep cache
```

### 배포 롤백

```bash
# 백업에서 복원
cd ~/backups
LATEST_BACKUP=$(ls -t | head -1)
cp -r $LATEST_BACKUP/* ~/en-sedaily/

# PM2 재시작
pm2 restart sedaily-eng
```

### 긴급 복구

```bash
# PM2 프로세스 강제 종료
pm2 kill

# 수동으로 시작
cd ~/en-sedaily
node server.js

# PM2 재설정
pm2 resurrect
```

---

## 📊 성능 최적화

### PM2 클러스터 모드

```javascript
// ecosystem.config.js
instances: 'max',  // CPU 코어 수만큼
exec_mode: 'cluster'
```

### Nginx 캐싱

```nginx
# /etc/nginx/sites-available/sedaily-eng
location /_next/static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Node.js 메모리 설정

```bash
# .env
NODE_OPTIONS="--max-old-space-size=1536"
```

---

## 💰 비용 예상

| 항목          | 사양        | 월 비용       |
| ------------- | ----------- | ------------- |
| EC2 t3.small  | 2 vCPU, 2GB | $15           |
| EBS Storage   | 20GB gp3    | $2            |
| Elastic IP    | 1개         | $3.6          |
| Data Transfer | ~100GB      | $9            |
| **총계**      |             | **약 $30/월** |

---

## 🔐 보안 체크리스트

- [ ] SSH 키 기반 인증만 허용
- [ ] Security Group 최소 권한
- [ ] 정기적인 시스템 업데이트
- [ ] SSL 인증서 자동 갱신
- [ ] PM2 로그 로테이션 설정
- [ ] CloudWatch 알람 설정
- [ ] 백업 자동화

---

## 📞 지원

문제 발생 시:

1. PM2 로그 확인: `pm2 logs`
2. Nginx 에러 로그: `/var/log/nginx/sedaily-error.log`
3. 시스템 로그: `journalctl -xe`

---

**작성일**: 2024-12-16  
**버전**: 1.0
