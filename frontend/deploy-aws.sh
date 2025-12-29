#!/bin/bash

# AWS CLI를 사용한 간단한 배포 스크립트
# Windows에서는 Git Bash에서 실행하세요

set -e

echo "🚀 Starting deployment..."

# 1. 빌드
echo "📦 Building application..."
npm run build

# 2. 배포 패키지 생성
echo "📁 Creating deployment package..."
rm -rf deploy-temp
mkdir deploy-temp

# 필수 파일들 복사
cp -r .next deploy-temp/
cp -r public deploy-temp/
cp package.json deploy-temp/
cp ecosystem.config.js deploy-temp/

# 3. 압축
echo "🗜️ Compressing files..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
tar -czf deploy-${TIMESTAMP}.tar.gz -C deploy-temp .

# 4. S3에 업로드
echo "☁️ Uploading to S3..."
aws s3 cp deploy-${TIMESTAMP}.tar.gz s3://seodaily-eng-frontend-dev-us-east-1/deploy/

# 5. EC2 인스턴스 ID 가져오기 (태그로 찾기)
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=sedaily-eng-server" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text)

if [ "$INSTANCE_ID" = "None" ] || [ -z "$INSTANCE_ID" ]; then
  echo "❌ EC2 instance not found. Please check the instance name tag."
  exit 1
fi

echo "🖥️ Found EC2 instance: $INSTANCE_ID"

# 6. EC2에서 배포 실행
echo "🔄 Deploying to EC2..."
COMMAND_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[
    'cd /home/ubuntu',
    'echo \"Stopping PM2...\"',
    'pm2 stop sedaily-eng || true',
    'echo \"Downloading deployment package...\"',
    'aws s3 cp s3://seodaily-eng-frontend-dev-us-east-1/deploy/deploy-${TIMESTAMP}.tar.gz ./',
    'echo \"Backing up current version...\"',
    'mv en-sedaily en-sedaily-backup-$(date +%Y%m%d-%H%M%S) || true',
    'echo \"Creating new directory...\"',
    'mkdir -p en-sedaily',
    'cd en-sedaily',
    'echo \"Extracting files...\"',
    'tar -xzf ../deploy-${TIMESTAMP}.tar.gz',
    'echo \"Starting PM2...\"',
    'pm2 start ecosystem.config.js',
    'pm2 save',
    'echo \"Deployment completed!\"',
    'pm2 status'
  ]" \
  --query "Command.CommandId" \
  --output text)

echo "📋 Command ID: $COMMAND_ID"
echo "⏳ Waiting for deployment to complete..."

# 7. 배포 상태 확인
sleep 5
aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID" \
  --query "StandardOutputContent" \
  --output text

# 8. 정리
echo "🧹 Cleaning up..."
rm -rf deploy-temp
rm deploy-${TIMESTAMP}.tar.gz

echo "✅ Deployment completed!"
echo "🌐 Website: https://en.sedaily.com"