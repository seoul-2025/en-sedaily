#!/bin/bash

###############################################################################
# Seoul Economic Daily - Infrastructure Metrics Dashboard
#
# 이 스크립트는 AWS CloudWatch에서 실시간 메트릭을 조회합니다.
# 대기업들이 사용하는 모니터링 방식을 참고하여 작성되었습니다.
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# AWS Region
REGION="us-east-1"

# Time range for metrics (last 5 minutes)
START_TIME=$(date -u -v-5M +"%Y-%m-%dT%H:%M:%S")
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Seoul Economic Daily - Infrastructure Metrics${NC}"
echo -e "${BLUE}   $(date)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

###############################################################################
# 1. CloudFront Metrics (CDN 트래픽)
###############################################################################
echo -e "${GREEN}📊 CloudFront (CDN) Metrics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get CloudFront Distribution ID
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --region us-east-1 \
  --query "DistributionList.Items[?Comment=='Seoul Economic Daily - EC2 SSR'].Id" \
  --output text 2>/dev/null)

if [ -n "$CLOUDFRONT_ID" ]; then
  echo "Distribution ID: $CLOUDFRONT_ID"

  # Total Requests (최근 5분)
  REQUESTS=$(aws cloudwatch get-metric-statistics \
    --region us-east-1 \
    --namespace AWS/CloudFront \
    --metric-name Requests \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} Total Requests (5분): ${GREEN}${REQUESTS}${NC} requests"

  # Bytes Downloaded (전송량)
  BYTES=$(aws cloudwatch get-metric-statistics \
    --region us-east-1 \
    --namespace AWS/CloudFront \
    --metric-name BytesDownloaded \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  # Convert to MB
  BYTES_MB=$(echo "scale=2; $BYTES / 1024 / 1024" | bc 2>/dev/null || echo "0")
  echo -e "  ${YELLOW}→${NC} Data Transfer (5분): ${GREEN}${BYTES_MB}${NC} MB"

  # 4xx Error Rate
  ERRORS_4XX=$(aws cloudwatch get-metric-statistics \
    --region us-east-1 \
    --namespace AWS/CloudFront \
    --metric-name 4xxErrorRate \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Average \
    --query 'Datapoints[0].Average' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} 4xx Error Rate: ${GREEN}${ERRORS_4XX}${NC}%"

  # 5xx Error Rate
  ERRORS_5XX=$(aws cloudwatch get-metric-statistics \
    --region us-east-1 \
    --namespace AWS/CloudFront \
    --metric-name 5xxErrorRate \
    --dimensions Name=DistributionId,Value=$CLOUDFRONT_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Average \
    --query 'Datapoints[0].Average' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} 5xx Error Rate: ${GREEN}${ERRORS_5XX}${NC}%"
else
  echo -e "${RED}CloudFront distribution not found${NC}"
fi

echo ""

###############################################################################
# 2. API Gateway Metrics (백엔드 API)
###############################################################################
echo -e "${GREEN}🔌 API Gateway Metrics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get API Gateway ID
API_ID=$(aws apigateway get-rest-apis \
  --region $REGION \
  --query "items[?name=='seodaily-eng-api-dev'].id" \
  --output text 2>/dev/null)

if [ -n "$API_ID" ]; then
  echo "API ID: $API_ID"

  # Total API Calls
  API_CALLS=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/ApiGateway \
    --metric-name Count \
    --dimensions Name=ApiName,Value=seodaily-eng-api-dev \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} API Calls (5분): ${GREEN}${API_CALLS}${NC} requests"

  # Average Latency
  LATENCY=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/ApiGateway \
    --metric-name Latency \
    --dimensions Name=ApiName,Value=seodaily-eng-api-dev \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Average \
    --query 'Datapoints[0].Average' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} Avg Latency: ${GREEN}${LATENCY}${NC} ms"

  # 4xx Errors
  API_4XX=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/ApiGateway \
    --metric-name 4XXError \
    --dimensions Name=ApiName,Value=seodaily-eng-api-dev \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} 4xx Errors: ${GREEN}${API_4XX}${NC} errors"

  # 5xx Errors
  API_5XX=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/ApiGateway \
    --metric-name 5XXError \
    --dimensions Name=ApiName,Value=seodaily-eng-api-dev \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} 5xx Errors: ${GREEN}${API_5XX}${NC} errors"
else
  echo -e "${RED}API Gateway not found${NC}"
fi

echo ""

###############################################################################
# 3. EC2 Instance Metrics (서버 상태)
###############################################################################
echo -e "${GREEN}🖥️  EC2 Instance Metrics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get EC2 Instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --region $REGION \
  --filters "Name=tag:Name,Values=sedaily-eng-production" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text 2>/dev/null)

if [ -n "$INSTANCE_ID" ] && [ "$INSTANCE_ID" != "None" ]; then
  echo "Instance ID: $INSTANCE_ID"

  # CPU Utilization
  CPU=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Average \
    --query 'Datapoints[0].Average' \
    --output text 2>/dev/null || echo "0")

  echo -e "  ${YELLOW}→${NC} CPU Utilization: ${GREEN}${CPU}${NC}%"

  # Network In
  NET_IN=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/EC2 \
    --metric-name NetworkIn \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  NET_IN_MB=$(echo "scale=2; $NET_IN / 1024 / 1024" | bc 2>/dev/null || echo "0")
  echo -e "  ${YELLOW}→${NC} Network In (5분): ${GREEN}${NET_IN_MB}${NC} MB"

  # Network Out
  NET_OUT=$(aws cloudwatch get-metric-statistics \
    --region $REGION \
    --namespace AWS/EC2 \
    --metric-name NetworkOut \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --start-time $START_TIME \
    --end-time $END_TIME \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

  NET_OUT_MB=$(echo "scale=2; $NET_OUT / 1024 / 1024" | bc 2>/dev/null || echo "0")
  echo -e "  ${YELLOW}→${NC} Network Out (5분): ${GREEN}${NET_OUT_MB}${NC} MB"

  # Status Check
  STATUS=$(aws ec2 describe-instance-status \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --query 'InstanceStatuses[0].InstanceStatus.Status' \
    --output text 2>/dev/null || echo "unknown")

  echo -e "  ${YELLOW}→${NC} Instance Status: ${GREEN}${STATUS}${NC}"
else
  echo -e "${RED}EC2 instance not found${NC}"
fi

echo ""

###############################################################################
# 4. Lambda Function Metrics (서버리스 함수)
###############################################################################
echo -e "${GREEN}⚡ Lambda Function Metrics${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# List of Lambda functions
LAMBDA_FUNCTIONS=("seodaily-eng-article-dev" "seodaily-eng-search-dev" "seodaily-eng-related-dev")

for FUNC_NAME in "${LAMBDA_FUNCTIONS[@]}"; do
  # Check if function exists
  if aws lambda get-function --function-name $FUNC_NAME --region $REGION &>/dev/null; then
    echo "Function: $FUNC_NAME"

    # Invocations
    INVOCATIONS=$(aws cloudwatch get-metric-statistics \
      --region $REGION \
      --namespace AWS/Lambda \
      --metric-name Invocations \
      --dimensions Name=FunctionName,Value=$FUNC_NAME \
      --start-time $START_TIME \
      --end-time $END_TIME \
      --period 300 \
      --statistics Sum \
      --query 'Datapoints[0].Sum' \
      --output text 2>/dev/null || echo "0")

    echo -e "  ${YELLOW}→${NC} Invocations (5분): ${GREEN}${INVOCATIONS}${NC} calls"

    # Errors
    ERRORS=$(aws cloudwatch get-metric-statistics \
      --region $REGION \
      --namespace AWS/Lambda \
      --metric-name Errors \
      --dimensions Name=FunctionName,Value=$FUNC_NAME \
      --start-time $START_TIME \
      --end-time $END_TIME \
      --period 300 \
      --statistics Sum \
      --query 'Datapoints[0].Sum' \
      --output text 2>/dev/null || echo "0")

    echo -e "  ${YELLOW}→${NC} Errors: ${RED}${ERRORS}${NC} errors"

    # Duration
    DURATION=$(aws cloudwatch get-metric-statistics \
      --region $REGION \
      --namespace AWS/Lambda \
      --metric-name Duration \
      --dimensions Name=FunctionName,Value=$FUNC_NAME \
      --start-time $START_TIME \
      --end-time $END_TIME \
      --period 300 \
      --statistics Average \
      --query 'Datapoints[0].Average' \
      --output text 2>/dev/null || echo "0")

    echo -e "  ${YELLOW}→${NC} Avg Duration: ${GREEN}${DURATION}${NC} ms"
    echo ""
  fi
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Metrics collection completed${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Save to log file
LOG_DIR="/Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/infrastructure/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/metrics_$(date +%Y%m%d_%H%M%S).log"
echo "Metrics saved to: $LOG_FILE"
