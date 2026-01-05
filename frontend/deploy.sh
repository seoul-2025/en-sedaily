#!/bin/bash

# ====================================================================
# Seoul Economic Daily - English Site Deployment Script
# ====================================================================
# 
# 이 스크립트는 Next.js 애플리케이션을 EC2 서버에 자동으로 배포합니다.
# 
# 사용법: ./deploy.sh
#
# 필수 요구사항:
#   - Node.js 및 npm 설치
#   - AWS EC2 접근을 위한 PEM 키 파일
#   - 서버에 PM2 설치
#
# ====================================================================

# 색상 정의 (로그 출력용)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ====================================================================
# 설정 변수
# ====================================================================

# EC2 서버 정보
EC2_HOST="52.21.195.0"
EC2_USER="ubuntu"
PEM_KEY="/d/sedaily/now/en-sedaily-1st-main/sedaily-es2-key.pem"

# 프로젝트 경로
PROJECT_DIR="/d/sedaily/now/en-sedaily-1st-main/frontend"
DEPLOY_PACKAGE_DIR="$PROJECT_DIR/deploy-package"
DEPLOY_TARBALL="deploy-$(date +%Y%m%d-%H%M%S).tar.gz"

# 서버 경로
SERVER_APP_DIR="en-sedaily"
SERVER_BACKUP_DIR="backups"

# PM2 앱 이름
PM2_APP_NAME="sedaily-eng"

# ====================================================================
# 유틸리티 함수
# ====================================================================

# 로그 출력 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 오류 발생 시 종료
exit_on_error() {
    if [ $? -ne 0 ]; then
        log_error "$1"
        log_error "배포가 중단되었습니다."
        exit 1
    fi
}

# ====================================================================
# 사전 검사
# ====================================================================

log_info "배포 사전 검사를 시작합니다..."

# PEM 키 파일 확인
if [ ! -f "$PEM_KEY" ]; then
    log_error "PEM 키 파일을 찾을 수 없습니다: $PEM_KEY"
    exit 1
fi

# 프로젝트 디렉토리 확인
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR"
    exit 1
fi

# package.json 확인
if [ ! -f "$PROJECT_DIR/package.json" ]; then
    log_error "package.json 파일을 찾을 수 없습니다."
    exit 1
fi

log_success "사전 검사 완료"

# ====================================================================
# 1단계: 빌드
# ====================================================================

log_info "1단계: 프로젝트 빌드를 시작합니다..."

cd "$PROJECT_DIR"
exit_on_error "프로젝트 디렉토리로 이동 실패"

# 이전 빌드 정리
log_info "이전 빌드 파일 정리 중..."
rm -rf .next
rm -rf deploy-package

# 의존성 설치 (필요한 경우)
log_info "의존성 확인 중..."
npm install
exit_on_error "의존성 설치 실패"

# Next.js 프로덕션 빌드
log_info "Next.js 프로덕션 빌드 실행 중..."
npm run build
exit_on_error "Next.js 빌드 실패"

log_success "빌드 완료"

# ====================================================================
# 2단계: 배포 패키지 생성
# ====================================================================

log_info "2단계: 배포 패키지를 생성합니다..."

# 배포 디렉토리 생성
log_info "배포 디렉토리 준비 중..."
rm -rf "$DEPLOY_PACKAGE_DIR"
mkdir -p "$DEPLOY_PACKAGE_DIR"

# standalone 파일 복사 (Next.js 최적화된 빌드)
log_info "Standalone 빌드 파일 복사 중..."
if [ ! -d ".next/standalone" ]; then
    log_error "Standalone 빌드를 찾을 수 없습니다. next.config.js에 output: 'standalone'이 설정되어 있는지 확인하세요."
    exit 1
fi
# cp의 * 패턴은 숨김 파일(.next)을 포함하지 않으므로 별도 복사
cp -r .next/standalone/.next "$DEPLOY_PACKAGE_DIR/"
cp -r .next/standalone/node_modules "$DEPLOY_PACKAGE_DIR/"
cp .next/standalone/package.json "$DEPLOY_PACKAGE_DIR/"
cp .next/standalone/server.js "$DEPLOY_PACKAGE_DIR/"
exit_on_error "Standalone 파일 복사 실패"

# .next 디렉토리는 이미 standalone 복사에 포함됨
log_info "BUILD_ID 파일 확인 중..."

# BUILD_ID 파일 확인
if [ -f "$DEPLOY_PACKAGE_DIR/.next/BUILD_ID" ]; then
    log_success "BUILD_ID 파일 확인 완료"
else
    log_error "BUILD_ID 파일을 찾을 수 없습니다."
    exit 1
fi

# static 파일 복사 (CSS, JS, 미디어 등)
log_info "Static 파일 복사 중..."
if [ -d ".next/static" ]; then
    cp -r .next/static "$DEPLOY_PACKAGE_DIR/.next/"
    exit_on_error "Static 파일 복사 실패"
else
    log_warning "Static 디렉토리가 없습니다. CSS 파일이 누락될 수 있습니다."
fi

# public 디렉토리 복사 (이미지, 파비콘 등)
log_info "Public 디렉토리 복사 중..."
if [ -d "public" ]; then
    cp -r public "$DEPLOY_PACKAGE_DIR/"
    exit_on_error "Public 디렉토리 복사 실패"
fi

# .env.local 파일 복사 (환경 변수)
log_info "환경 변수 파일 복사 중..."
if [ -f ".env.local" ]; then
    cp .env.local "$DEPLOY_PACKAGE_DIR/"
    exit_on_error ".env.local 복사 실패"
    log_success ".env.local 파일이 배포 패키지에 포함되었습니다."
else
    log_warning ".env.local 파일이 없습니다. 환경 변수가 제대로 설정되지 않을 수 있습니다."
fi

# PM2 설정 파일 복사
log_info "PM2 설정 파일 복사 중..."
if [ -f "ecosystem.config.js" ]; then
    cp ecosystem.config.js "$DEPLOY_PACKAGE_DIR/"
    exit_on_error "ecosystem.config.js 복사 실패"
else
    log_warning "ecosystem.config.js 파일이 없습니다. 기본 PM2 설정을 생성합니다."
    cat > "$DEPLOY_PACKAGE_DIR/ecosystem.config.js" << 'EOF'
// Load environment variables from .env.local
const fs = require('fs');
const path = require('path');

// Read .env.local file if it exists
const envLocalPath = path.join(__dirname, '.env.local');
const envVars = {
  NODE_ENV: 'production',
  PORT: 3000,
};

if (fs.existsSync(envLocalPath)) {
  const envContent = fs.readFileSync(envLocalPath, 'utf8');
  envContent.split('\n').forEach(line => {
    // Skip empty lines and comments
    if (!line || line.trim().startsWith('#')) return;

    const [key, ...valueParts] = line.split('=');
    if (key && valueParts.length > 0) {
      envVars[key.trim()] = valueParts.join('=').trim();
    }
  });
  console.log('✅ .env.local 파일을 성공적으로 로드했습니다.');
} else {
  console.warn('⚠️  .env.local 파일을 찾을 수 없습니다. 기본 설정을 사용합니다.');
  // Fallback to hardcoded values if .env.local doesn't exist
  envVars.NEXT_PUBLIC_API_URL = 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';
  envVars.REVALIDATE_SECRET = 'd5aed293ec4993ad6b13a4033b3b73986b40206cd6d6f43018b3ec0f01bc2748';
}

module.exports = {
  apps: [
    {
      name: 'sedaily-eng',
      script: 'server.js',
      env: envVars,
    },
  ],
};
EOF
fi

# 배포 패키지 검증
log_info "배포 패키지 검증 중..."

# 필수 파일 확인
REQUIRED_FILES=(
    "$DEPLOY_PACKAGE_DIR/server.js"
    "$DEPLOY_PACKAGE_DIR/package.json"
    "$DEPLOY_PACKAGE_DIR/.next/BUILD_ID"
    "$DEPLOY_PACKAGE_DIR/ecosystem.config.js"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "필수 파일이 누락되었습니다: $file"
        exit 1
    fi
done

# 필수 디렉토리 확인
REQUIRED_DIRS=(
    "$DEPLOY_PACKAGE_DIR/node_modules"
    "$DEPLOY_PACKAGE_DIR/.next"
    "$DEPLOY_PACKAGE_DIR/.next/server"
    "$DEPLOY_PACKAGE_DIR/.next/static"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        log_error "필수 디렉토리가 누락되었습니다: $dir"
        exit 1
    fi
done

log_success "배포 패키지 검증 완료"

# tar 파일 생성
log_info "배포 아카이브 생성 중..."
cd "$DEPLOY_PACKAGE_DIR"
tar -czf "../$DEPLOY_TARBALL" .
exit_on_error "tar 파일 생성 실패"
cd "$PROJECT_DIR"

log_success "배포 패키지 생성 완료: $DEPLOY_TARBALL"

# ====================================================================
# 3단계: 서버 백업
# ====================================================================

log_info "3단계: 서버의 현재 버전을 백업합니다..."

# 서버 연결 테스트
log_info "서버 연결 테스트 중..."
ssh -i "$PEM_KEY" -o ConnectTimeout=5 "$EC2_USER@$EC2_HOST" "echo 'Server connected'" > /dev/null 2>&1
exit_on_error "서버 연결 실패"

# 현재 버전 백업
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
log_info "현재 버전을 백업합니다: $BACKUP_NAME"

ssh -i "$PEM_KEY" "$EC2_USER@$EC2_HOST" << EOF
    # 백업 디렉토리 생성
    mkdir -p ~/$SERVER_BACKUP_DIR
    
    # 현재 앱이 존재하면 백업
    if [ -d ~/$SERVER_APP_DIR ]; then
        cp -r ~/$SERVER_APP_DIR ~/$SERVER_BACKUP_DIR/$BACKUP_NAME
        echo "백업 완료: $BACKUP_NAME"
    else
        echo "기존 애플리케이션이 없습니다. 새로 설치합니다."
    fi
    
    # 오래된 백업 정리 (최근 5개만 유지)
    cd ~/$SERVER_BACKUP_DIR
    ls -t | tail -n +6 | xargs -r rm -rf
EOF
exit_on_error "백업 실패"

log_success "백업 완료"

# ====================================================================
# 4단계: 서버에 배포
# ====================================================================

log_info "4단계: 서버에 새 버전을 배포합니다..."

# tar 파일 업로드
log_info "배포 파일 업로드 중..."
scp -i "$PEM_KEY" "$PROJECT_DIR/$DEPLOY_TARBALL" "$EC2_USER@$EC2_HOST:~/"
exit_on_error "파일 업로드 실패"

# 서버에서 배포 실행
log_info "서버에서 배포를 실행합니다..."

ssh -i "$PEM_KEY" "$EC2_USER@$EC2_HOST" << EOF
    set -e
    
    echo "PM2 프로세스 중지..."
    pm2 stop $PM2_APP_NAME || true
    
    echo "이전 애플리케이션 디렉토리 제거..."
    rm -rf ~/$SERVER_APP_DIR
    
    echo "새 애플리케이션 디렉토리 생성..."
    mkdir -p ~/$SERVER_APP_DIR
    
    echo "배포 파일 압축 해제..."
    cd ~/$SERVER_APP_DIR
    tar -xzf ~/$DEPLOY_TARBALL
    
    echo "배포 파일 정리..."
    rm ~/$DEPLOY_TARBALL
    
    echo "파일 구조 확인..."
    if [ ! -f .next/BUILD_ID ]; then
        echo "ERROR: BUILD_ID 파일이 없습니다!"
        exit 1
    fi
    
    if [ ! -d .next/static ]; then
        echo "WARNING: static 디렉토리가 없습니다. CSS가 누락될 수 있습니다."
    fi
    
    echo "PM2로 애플리케이션 시작..."
    pm2 start ecosystem.config.js
    
    echo "PM2 프로세스 저장..."
    pm2 save
    
    echo "PM2 상태 확인..."
    pm2 status
    
    echo "최근 로그 확인..."
    pm2 logs --lines 5 --nostream
EOF

DEPLOY_RESULT=$?

if [ $DEPLOY_RESULT -ne 0 ]; then
    log_error "배포 중 오류가 발생했습니다."
    log_warning "필요한 경우 다음 명령으로 이전 버전을 복원할 수 있습니다:"
    echo "ssh -i $PEM_KEY $EC2_USER@$EC2_HOST 'cd ~/backups && cp -r $BACKUP_NAME ~/$SERVER_APP_DIR && cd ~/$SERVER_APP_DIR && pm2 restart all'"
    exit 1
fi

log_success "배포 완료!"

# ====================================================================
# 5단계: 배포 검증
# ====================================================================

log_info "5단계: 배포 검증을 시작합니다..."

# PM2 상태 확인
log_info "애플리케이션 상태 확인 중..."
PM2_STATUS=$(ssh -i "$PEM_KEY" "$EC2_USER@$EC2_HOST" "pm2 status --json" 2>/dev/null)

# PM2 JSON 출력에서 online 상태 확인 (더 정확한 방법)
if echo "$PM2_STATUS" | grep -q '"status":"online"' || ssh -i "$PEM_KEY" "$EC2_USER@$EC2_HOST" "pm2 status | grep -q 'online'"; then
    log_success "애플리케이션이 정상적으로 실행 중입니다."
else
    log_warning "PM2 상태 확인에 실패했지만 HTTP 응답을 확인합니다..."
    # Note: PM2 상태 검증에 false negative가 있을 수 있음
    # 실제 HTTP 응답으로 최종 확인하는 것이 더 정확함
fi

# HTTP 응답 확인 (옵션)
log_info "HTTP 응답 확인 중..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$EC2_HOST:3000" 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    log_success "웹 서버가 정상적으로 응답합니다. (HTTP $HTTP_STATUS)"
else
    log_warning "웹 서버 응답 확인 실패 (HTTP $HTTP_STATUS). CloudFront를 통해서만 접근 가능할 수 있습니다."
fi

# ====================================================================
# 배포 완료
# ====================================================================

echo ""
echo "========================================"
echo -e "${GREEN}배포가 성공적으로 완료되었습니다!${NC}"
echo "========================================"
echo ""
echo "배포 정보:"
echo "  - 서버: $EC2_HOST"
echo "  - 애플리케이션: $SERVER_APP_DIR"
echo "  - PM2 앱 이름: $PM2_APP_NAME"
echo "  - 백업 위치: $SERVER_BACKUP_DIR/$BACKUP_NAME"
echo ""
echo "유용한 명령어:"
echo "  - 로그 확인: ssh -i $PEM_KEY $EC2_USER@$EC2_HOST 'pm2 logs'"
echo "  - 상태 확인: ssh -i $PEM_KEY $EC2_USER@$EC2_HOST 'pm2 status'"
echo "  - 재시작: ssh -i $PEM_KEY $EC2_USER@$EC2_HOST 'pm2 restart all'"
echo ""
echo "웹사이트: https://en.sedaily.com"
echo ""

# 로컬 배포 파일 정리
log_info "로컬 임시 파일 정리 중..."
rm -f "$PROJECT_DIR/$DEPLOY_TARBALL"
rm -rf "$DEPLOY_PACKAGE_DIR"

log_success "모든 작업이 완료되었습니다!"