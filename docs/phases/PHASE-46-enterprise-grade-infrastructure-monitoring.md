# Phase 46: Enterprise-Grade Infrastructure Monitoring

**Timeline:** 2025-12-31
**Status:** ✅ Completed

---

## Overview

Implemented professional infrastructure monitoring and alerting system using AWS CloudWatch Dashboard + Alarms + SNS notifications (enterprise standard). This provides real-time visibility into traffic, performance, costs, and automated alerts before issues impact users.

**Impact**: Production infrastructure now monitored with 8 automated alarms, 6-row visual dashboard, and email notifications for critical issues.

---

## Before: No Monitoring

### Problem

```
❌ No visibility into infrastructure health
❌ No alerts when servers overload or crash
❌ No performance metrics (response times, error rates)
❌ No cost tracking (AWS bill surprises)
❌ Reactive problem-solving (users complain first)
```

### Infrastructure Blindness

Without monitoring, the team had NO answers to critical questions:

- **Traffic**: How many requests are we serving? Is traffic growing?
- **Performance**: Are APIs responding quickly? Is CloudFront caching effectively?
- **Errors**: Are there 5xx errors? Where are they coming from?
- **Capacity**: Is EC2 CPU usage approaching limits? Do we need to scale?
- **Costs**: How much is AWS costing us this month? Are we overspending?

### Business Risk

**High risk of undetected outages:**
- EC2 instance crashes → No one knows until users complain
- API latency spikes to 5s → No visibility into performance degradation
- CloudFront 5xx errors → Traffic served with errors, no alerts
- AWS bill hits $500 → No budget warnings, unexpected costs

---

## After: Enterprise-Grade Monitoring System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MONITORING ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐  │
│  │CloudFront│   │    API   │   │   EC2    │   │ Lambda  │  │
│  │   (CDN)  │   │ Gateway  │   │ (Server) │   │Functions│  │
│  └─────┬────┘   └─────┬────┘   └─────┬────┘   └────┬────┘  │
│        │              │              │              │        │
│        └──────────────┴──────────────┴──────────────┘        │
│                          │                                   │
│                    ┌─────▼─────┐                             │
│                    │ CloudWatch│                             │
│                    │  Metrics  │                             │
│                    └─────┬─────┘                             │
│                          │                                   │
│          ┌───────────────┼───────────────┐                  │
│          │               │               │                  │
│     ┌────▼────┐    ┌────▼────┐    ┌────▼────┐              │
│     │Dashboard│    │ Alarms  │    │  Logs   │              │
│     │(Visual) │    │(Alerts) │    │ (Debug) │              │
│     └─────────┘    └────┬────┘    └─────────┘              │
│                         │                                   │
│                    ┌────▼────┐                              │
│                    │   SNS   │                              │
│                    │  Topic  │                              │
│                    └────┬────┘                              │
│                         │                                   │
│                    ┌────▼────┐                              │
│                    │  Email  │                              │
│                    │ Alerts  │                              │
│                    └─────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### Solution Components

✅ **CloudWatch Dashboard** - Visual metrics (6 rows of charts)
✅ **CloudWatch Alarms** - Automated alerts (8 critical thresholds)
✅ **SNS Notifications** - Email alerts to operations team
✅ **CLI Metrics Script** - Real-time metrics viewer

---

## Part 1: CloudWatch Dashboard

### Visual Monitoring (6 Rows of Metrics)

**File:** `infrastructure/modules/monitoring/cloudwatch_dashboard.tf`

#### Row 1: CloudFront (CDN Performance)

```hcl
# Total Requests (Traffic Volume)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/CloudFront", "Requests", { stat = "Sum", label = "총 요청 수" }]
    ]
    title   = "📊 CloudFront - 총 요청 수 (Requests)"
    period  = 300  # 5-minute intervals
  }
}

# Data Transfer (Bandwidth Usage)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/CloudFront", "BytesDownloaded", { stat = "Sum", label = "다운로드 데이터" }],
      [".", "BytesUploaded", { stat = "Sum", label = "업로드 데이터" }]
    ]
    title   = "📡 CloudFront - 데이터 전송량 (Bytes)"
  }
}
```

**Metrics Tracked:**
- ✅ Total requests (traffic volume)
- ✅ Data transfer (download/upload bytes)
- ✅ 4xx/5xx error rates
- ✅ Cache hit rate (performance efficiency)
- ✅ Origin latency (backend response time)

#### Row 2: CloudFront Error Rates

```hcl
# Error Rates (4xx/5xx)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/CloudFront", "4xxErrorRate", { stat = "Average", label = "4xx 에러율", color = "#ff7f0e" }],
      [".", "5xxErrorRate", { stat = "Average", label = "5xx 에러율", color = "#d62728" }]
    ]
    title   = "⚠️ CloudFront - 에러율 (%)"
    yAxis = {
      left = {
        label = "Error Rate (%)"
        min   = 0
      }
    }
  }
}

# Cache Hit Rate (Efficiency)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/CloudFront", "CacheHitRate", { stat = "Average", label = "캐시 적중률" }]
    ]
    title   = "💾 CloudFront - 캐시 적중률 (%)"
    yAxis = {
      left = {
        min   = 0
        max   = 100
      }
    }
  }
}
```

#### Row 3: API Gateway (Backend Performance)

```hcl
# API Call Volume
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/ApiGateway", "Count", { stat = "Sum", label = "API 호출 수" }]
    ]
    title   = "🔌 API Gateway - 총 호출 수"
  }
}

# Response Times (Latency)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/ApiGateway", "Latency", { stat = "Average", label = "평균 지연시간" }],
      [".", "IntegrationLatency", { stat = "Average", label = "Lambda 실행시간" }]
    ]
    title   = "⏱️ API Gateway - 응답 시간 (ms)"
  }
}

# API Errors (4xx/5xx)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/ApiGateway", "4XXError", { stat = "Sum", label = "4xx 에러" }],
      [".", "5XXError", { stat = "Sum", label = "5xx 에러" }]
    ]
    title   = "❌ API Gateway - 에러 수"
    stacked = true
  }
}
```

**Metrics Tracked:**
- ✅ Total API calls (usage volume)
- ✅ Average latency (user experience)
- ✅ Integration latency (Lambda execution time)
- ✅ 4xx errors (client issues)
- ✅ 5xx errors (backend failures)

#### Row 4: EC2 Instance (Server Health)

```hcl
# CPU Utilization (Server Load)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/EC2", "CPUUtilization", { stat = "Average", label = "CPU 사용률" }]
    ]
    title   = "🖥️ EC2 - CPU 사용률 (%)"
    yAxis = {
      left = {
        min   = 0
        max   = 100
      }
    }
    annotations = {
      horizontal = [
        {
          label = "경고 임계값"
          value = 80
          fill  = "above"
          color = "#ff7f0e"
        },
        {
          label = "위험 임계값"
          value = 90
          fill  = "above"
          color = "#d62728"
        }
      ]
    }
  }
}

# Network Traffic (Bandwidth)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/EC2", "NetworkIn", { stat = "Sum", label = "Network In" }],
      [".", "NetworkOut", { stat = "Sum", label = "Network Out" }]
    ]
    title   = "🌐 EC2 - 네트워크 트래픽 (Bytes)"
  }
}

# Status Checks (Instance Health)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/EC2", "StatusCheckFailed", { stat = "Sum", label = "상태 체크 실패" }],
      [".", "StatusCheckFailed_Instance", { stat = "Sum", label = "인스턴스 체크 실패" }],
      [".", "StatusCheckFailed_System", { stat = "Sum", label = "시스템 체크 실패" }]
    ]
    title   = "🔍 EC2 - 상태 체크"
    stacked = true
  }
}
```

**Metrics Tracked:**
- ✅ CPU utilization (with 80%/90% warning thresholds)
- ✅ Network in/out (traffic volume)
- ✅ Status check failures (instance/system health)

#### Row 5: Lambda Functions (Serverless Performance)

```hcl
# Lambda Invocations (Function Calls)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Lambda 실행 수" }]
    ]
    title   = "⚡ Lambda - 총 실행 수"
  }
}

# Execution Duration (Performance)
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/Lambda", "Duration", { stat = "Average", label = "평균 실행시간" }],
      [".", "Duration", { stat = "Maximum", label = "최대 실행시간" }]
    ]
    title   = "⏱️ Lambda - 실행 시간 (ms)"
  }
}

# Lambda Errors & Throttles
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/Lambda", "Errors", { stat = "Sum", label = "에러", color = "#d62728" }],
      [".", "Throttles", { stat = "Sum", label = "제한", color = "#ff7f0e" }]
    ]
    title   = "❌ Lambda - 에러 & 제한"
    stacked = true
  }
}
```

**Metrics Tracked:**
- ✅ Total invocations (function usage)
- ✅ Average/max duration (execution time)
- ✅ Errors (function failures)
- ✅ Throttles (concurrency limits hit)

#### Row 6: AWS Billing (Cost Tracking)

```hcl
# Estimated Monthly Charges
{
  type = "metric"
  properties = {
    metrics = [
      ["AWS/Billing", "EstimatedCharges", { stat = "Maximum", label = "예상 비용 (USD)" }]
    ]
    view    = "singleValue"  # Large number display
    title   = "💰 AWS 월별 예상 비용 (USD)"
    period  = 86400  # Daily updates
  }
}
```

**Metrics Tracked:**
- ✅ Monthly estimated AWS charges (real-time cost tracking)

### Dashboard URL

```hcl
output "cloudwatch_dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}
```

**Access:** AWS Console → CloudWatch → Dashboards → `seodaily-eng-infrastructure-dashboard`

---

## Part 2: CloudWatch Alarms (Automated Alerts)

### 8 Critical Alarms with SNS Email Notifications

**File:** `infrastructure/modules/monitoring/cloudwatch_alarms.tf`

#### Alarm 1: EC2 CPU High (Server Overload)

```hcl
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "${var.project_name}-ec2-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300  # 5 minutes
  statistic           = "Average"
  threshold           = 80   # 80% CPU
  alarm_description   = "EC2 CPU 사용률이 80%를 초과했습니다. 서버 증설을 고려하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    InstanceId = var.ec2_instance_id
  }

  tags = {
    Severity = "High"
  }
}
```

**Trigger:** CPU > 80% for 10 minutes (2 × 5min periods)
**Action:** Email alert → "Server overload, consider scaling"
**Severity:** High

#### Alarm 2: EC2 Status Check Failed (Server Down)

```hcl
resource "aws_cloudwatch_metric_alarm" "ec2_status_check_failed" {
  alarm_name          = "${var.project_name}-ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60   # 1 minute
  statistic           = "Maximum"
  threshold           = 0    # Any failure triggers alarm
  alarm_description   = "EC2 인스턴스 상태 체크 실패! 즉시 확인이 필요합니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  tags = {
    Severity = "Critical"
  }
}
```

**Trigger:** Any status check failure for 2 minutes
**Action:** Email alert → "EC2 instance down! Immediate action required"
**Severity:** Critical

#### Alarm 3: API Gateway 5xx Errors (Backend Issues)

```hcl
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${var.project_name}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 10   # More than 10 errors
  alarm_description   = "API Gateway에서 5xx 에러가 10개 이상 발생했습니다. 백엔드를 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  tags = {
    Severity = "High"
  }
}
```

**Trigger:** > 10 × 5xx errors in 10 minutes
**Action:** Email alert → "Backend errors detected, check API"
**Severity:** High

#### Alarm 4: API Gateway High Latency (Performance Degradation)

```hcl
resource "aws_cloudwatch_metric_alarm" "api_high_latency" {
  alarm_name          = "${var.project_name}-api-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Average"
  threshold           = 3000  # 3 seconds
  alarm_description   = "API 평균 응답시간이 3초를 초과했습니다. 성능 최적화가 필요합니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  tags = {
    Severity = "Medium"
  }
}
```

**Trigger:** Average API latency > 3s for 15 minutes
**Action:** Email alert → "API slow, performance optimization needed"
**Severity:** Medium

#### Alarm 5: Lambda Errors (Function Failures)

```hcl
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = length(var.lambda_function_names)
  alarm_name          = "${var.project_name}-lambda-${var.lambda_function_names[count.index]}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5    # More than 5 errors
  alarm_description   = "Lambda 함수 ${var.lambda_function_names[count.index]}에서 에러가 5개 이상 발생했습니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    FunctionName = var.lambda_function_names[count.index]
  }

  tags = {
    Severity = "Medium"
  }
}
```

**Trigger:** > 5 Lambda errors in 10 minutes (per function)
**Action:** Email alert → "Lambda function failing, check logs"
**Severity:** Medium

#### Alarm 6: CloudFront 5xx Errors (CDN Issues)

```hcl
resource "aws_cloudwatch_metric_alarm" "cloudfront_5xx_errors" {
  alarm_name          = "${var.project_name}-cloudfront-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 5    # 5% error rate
  alarm_description   = "CloudFront 5xx 에러율이 5%를 초과했습니다. Origin 서버를 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  tags = {
    Severity = "High"
  }
}
```

**Trigger:** CloudFront 5xx error rate > 5% for 10 minutes
**Action:** Email alert → "CDN errors detected, check origin server"
**Severity:** High

#### Alarm 7: CloudFront Cache Hit Rate Low (Cache Misconfiguration)

```hcl
resource "aws_cloudwatch_metric_alarm" "cloudfront_cache_hit_low" {
  alarm_name          = "${var.project_name}-cloudfront-cache-hit-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CacheHitRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 50   # 50% cache hit rate
  alarm_description   = "CloudFront 캐시 적중률이 50% 미만입니다. 캐시 설정을 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  tags = {
    Severity = "Low"
  }
}
```

**Trigger:** Cache hit rate < 50% for 15 minutes
**Action:** Email alert → "Low cache efficiency, check CloudFront config"
**Severity:** Low

#### Alarm 8: AWS Cost Budget (Budget Overrun)

```hcl
resource "aws_cloudwatch_metric_alarm" "estimated_charges" {
  alarm_name          = "${var.project_name}-estimated-charges-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400  # Daily check
  statistic           = "Maximum"
  threshold           = 100    # $100 USD
  alarm_description   = "AWS 월별 예상 비용이 $100를 초과했습니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    Currency = "USD"
  }

  tags = {
    Severity = "Medium"
  }
}
```

**Trigger:** Monthly AWS bill > $100
**Action:** Email alert → "Budget exceeded, review costs"
**Severity:** Medium

### SNS Topic & Email Subscription

```hcl
# SNS Topic for alarms
resource "aws_sns_topic" "alarms" {
  name  = "${var.project_name}-cloudwatch-alarms"
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alert_email  # Operations team email
}
```

**Setup:** When Terraform applies, AWS sends confirmation email → Click "Confirm subscription"

---

## Part 3: CLI Metrics Script

### Real-Time Metrics Viewer

**File:** `infrastructure/scripts/check_metrics.sh`

```bash
#!/bin/bash
# Seoul Economic Daily - Infrastructure Metrics Dashboard

# Time range for metrics (last 5 minutes)
START_TIME=$(date -u -v-5M +"%Y-%m-%dT%H:%M:%S")
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

# 1. CloudFront Metrics (CDN Traffic)
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?Comment=='Seoul Economic Daily - EC2 SSR'].Id" \
  --output text)

# Total Requests (최근 5분)
REQUESTS=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=$CLOUDFRONT_ID \
  --start-time $START_TIME \
  --end-time $END_TIME \
  --period 300 \
  --statistics Sum \
  --query 'Datapoints[0].Sum' \
  --output text)

echo "→ Total Requests (5분): ${REQUESTS} requests"

# 2. API Gateway Metrics
API_CALLS=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=seodaily-eng-api-dev \
  --start-time $START_TIME \
  --end-time $END_TIME \
  --period 300 \
  --statistics Sum \
  --query 'Datapoints[0].Sum' \
  --output text)

echo "→ API Calls (5분): ${API_CALLS} requests"

# 3. EC2 Instance Metrics
CPU=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time $START_TIME \
  --end-time $END_TIME \
  --period 300 \
  --statistics Average \
  --query 'Datapoints[0].Average' \
  --output text)

echo "→ CPU Utilization: ${CPU}%"
```

**Usage:**

```bash
# View real-time metrics (last 5 minutes)
./infrastructure/scripts/check_metrics.sh
```

**Output Example:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Seoul Economic Daily - Infrastructure Metrics
   Wed Dec 31 14:25:03 KST 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CloudFront (CDN) Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Distribution ID: E1ABCDEF123456
  → Total Requests (5분): 15,234 requests
  → Data Transfer (5분): 234.56 MB
  → 4xx Error Rate: 0.5%
  → 5xx Error Rate: 0.0%

🔌 API Gateway Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API ID: 7w5nco7xn4
  → API Calls (5분): 1,243 requests
  → Avg Latency: 245.3 ms
  → 4xx Errors: 12 errors
  → 5xx Errors: 0 errors

🖥️ EC2 Instance Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instance ID: i-0123456789abcdef
  → CPU Utilization: 23.4%
  → Network In (5분): 45.2 MB
  → Network Out (5분): 123.7 MB
  → Instance Status: ok

⚡ Lambda Function Metrics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Function: seodaily-eng-article-dev
  → Invocations (5분): 523 calls
  → Errors: 0 errors
  → Avg Duration: 187.5 ms

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Metrics collection completed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Monitoring Philosophy (Fortune 500 Standard)

### Tier 1: AWS CloudWatch (FREE) ← **We Implemented This**

**What we built:**
- ✅ CloudWatch Dashboard - Visual metrics (6 rows)
- ✅ CloudWatch Alarms - Automated alerts (8 critical thresholds)
- ✅ SNS Notifications - Email alerts to operations team
- ✅ CLI Metrics Script - Real-time command-line viewer

**Cost:** $0 (within free tier limits)
**Suitable for:** Small-medium projects, startups, MVPs

### Tier 2: APM Solutions ($100-500/month)

**Examples:** Datadog, New Relic, Dynatrace
**Features:**
- Advanced APM (application performance monitoring)
- Distributed tracing
- Custom dashboards
- Mobile app monitoring

**When to upgrade:** > 1M requests/day, > 10 microservices

### Tier 3: Self-Hosted Monitoring (DIY)

**Examples:** Grafana + Prometheus
**Features:**
- Full control
- Unlimited metrics
- No vendor lock-in

**Cost:** Infrastructure + maintenance time
**When to use:** Enterprise with dedicated DevOps team

---

## Business Value

### Proactive Problem Detection

**Before:** Users complain → Investigate → Fix (hours of downtime)
**After:** Alert triggers → Investigate → Fix (minutes of downtime)

**Example Alert Flow:**

```
1. EC2 CPU hits 85% → Alarm triggers
2. Email sent to operations team
3. Team investigates: Traffic spike from viral article
4. Scale EC2 instance size (t3.medium → t3.large)
5. CPU drops to 45%
6. Crisis averted before users experience slowdown
```

### Data-Driven Scaling Decisions

**Questions we can now answer:**

- **"Do we need to scale?"** → Check CPU trend over 7 days
- **"Is CloudFront caching effective?"** → Check cache hit rate (target: >85%)
- **"Which API endpoint is slowest?"** → Check integration latency
- **"Are we overspending on AWS?"** → Check billing dashboard daily

### Cost Control

**Monthly Cost Tracking:**
- ✅ Real-time AWS bill visibility
- ✅ Email alert when budget exceeded ($100 threshold)
- ✅ Prevent unexpected $500 AWS bills

### Performance Optimization

**Response Time Monitoring:**
- ✅ API latency trends (target: <500ms)
- ✅ Lambda execution time (target: <200ms)
- ✅ CloudFront origin latency (target: <100ms)

---

## Files Added/Modified

### Terraform Modules

1. **`infrastructure/modules/monitoring/cloudwatch_dashboard.tf`** - Visual dashboard (6 rows, 392 lines)
2. **`infrastructure/modules/monitoring/cloudwatch_alarms.tf`** - 8 automated alarms (261 lines)
3. **`infrastructure/modules/monitoring/cloudwatch_logs.tf`** - Log groups configuration
4. **`infrastructure/modules/monitoring/variables.tf`** - Module input variables
5. **`infrastructure/modules/monitoring/outputs.tf`** - Module outputs (dashboard URL, alarm ARNs)

### Scripts

6. **`infrastructure/scripts/check_metrics.sh`** - CLI metrics viewer (341 lines)

### Configuration

```hcl
# Example Terraform usage
module "monitoring" {
  source = "./modules/monitoring"

  project_name              = "seodaily-eng"
  environment               = "production"
  region                    = "us-east-1"
  ec2_instance_id           = "i-0123456789abcdef"
  api_gateway_id            = "7w5nco7xn4"
  cloudfront_distribution_id = "E1ABCDEF123456"
  lambda_function_names     = ["seodaily-eng-article-dev", "seodaily-eng-search-dev"]
  alert_email               = "devops@sedaily.com"
}
```

---

## Next Steps (Optional Enhancements)

### Near-Term (< 1 month)

1. **PM2 Cluster Mode** - Zero-downtime deployments (easiest option)
   ```bash
   pm2 start ecosystem.config.js --env production
   pm2 reload all  # Rolling restart, no downtime
   ```

2. **Custom Metrics** - Application-specific tracking
   - Article page views
   - Search queries per minute
   - Translation API success rate

### Long-Term (> 3 months)

3. **Application Load Balancer (ALB)** - Multi-instance architecture
   - Health checks
   - Auto-scaling groups
   - Blue-green deployments

4. **Auto Scaling** - Dynamic capacity management
   - Scale up during traffic spikes
   - Scale down during low usage
   - Cost optimization

---

## Result

Enterprise-grade monitoring system operational:
- ✅ **8 automated alarms** with email notifications
- ✅ **6-row visual dashboard** (CloudFront, API, EC2, Lambda, Billing)
- ✅ **Real-time metrics** via CLI script
- ✅ **Proactive alerting** before users experience issues
- ✅ **$0 cost** (within AWS free tier)

**Impact:** Production infrastructure now fully observable with professional monitoring standards.

---

## Summary (Original Bullet Points)

*This section preserves the original 66-line Phase 46 documentation.*

- **Goal**: Implement professional infrastructure monitoring and alerting system
- **Business Need**: Monitor traffic, performance, costs, and get alerts before issues impact users
- **Strategy**: AWS CloudWatch Dashboard + Alarms + SNS notifications (enterprise standard)
- **Implementation**:
  - Created real-time metrics collection script `infrastructure/scripts/check_metrics.sh`
  - Built comprehensive CloudWatch Dashboard (6 rows of metrics)
  - Set up 8 CloudWatch Alarms with SNS email notifications
  - Configured monitoring for CloudFront, API Gateway, EC2, Lambda, and AWS billing
- **Files Added**:
  - `infrastructure/scripts/check_metrics.sh` - CLI metrics viewer (CloudFront, API, EC2, Lambda)
  - `infrastructure/modules/monitoring/cloudwatch_dashboard.tf` - Visual dashboard
  - `infrastructure/modules/monitoring/cloudwatch_alarms.tf` - Automated alerts
  - `infrastructure/modules/monitoring/variables.tf` - Module configuration
  - `infrastructure/modules/monitoring/outputs.tf` - Module outputs
- **Dashboard Metrics** (What big companies monitor):
  - **CloudFront**: Total requests, data transfer, error rates (4xx/5xx), cache hit rate, origin latency
  - **API Gateway**: Total calls, average latency, integration latency, 4xx/5xx errors
  - **EC2**: CPU utilization, network traffic, status checks
  - **Lambda**: Invocations, execution duration, errors, throttles
  - **Billing**: Monthly estimated charges
- **Automated Alarms** (Critical/High/Medium severity):
  - EC2 CPU > 80% → Email alert (server overload)
  - EC2 Status Check Failed → Email alert (server down - CRITICAL)
  - API 5xx errors > 10 → Email alert (backend issues)
  - API latency > 3s → Email alert (performance degradation)
  - Lambda errors > 5 → Email alert (function failures)
  - CloudFront 5xx rate > 5% → Email alert (CDN issues)
  - CloudFront cache hit rate < 50% → Email alert (cache misconfiguration)
  - AWS monthly cost > $100 → Email alert (budget overrun)
- **Monitoring Philosophy** (How Fortune 500 companies do it):
  - **Tier 1** (Free): AWS CloudWatch Dashboard + Alarms ← **We implemented this**
  - **Tier 2** ($100-500/mo): Datadog, New Relic (APM solutions)
  - **Tier 3** (DIY): Grafana + Prometheus (self-hosted)
- **Usage**:
  ```bash
  # View real-time metrics (last 5 minutes)
  ./infrastructure/scripts/check_metrics.sh

  # CloudWatch Dashboard URL (visual charts)
  # Output: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=seodaily-eng-infrastructure-dashboard

  # Email alerts automatically sent when thresholds exceeded
  ```
- **Business Value**:
  - **Proactive**: Detect issues before users complain
  - **Data-Driven**: Make scaling decisions based on actual traffic data
  - **Cost Control**: Get alerted when AWS bill exceeds budget
  - **Performance**: Monitor response times and optimize bottlenecks
- **Next Steps** (Optional enhancements):
  - Application Load Balancer (ALB) for zero-downtime deployments
  - Auto Scaling Groups based on traffic patterns
  - PM2 Cluster Mode for EC2 (easiest zero-downtime option)
- **Result**: Enterprise-grade monitoring system operational

---

**Related Documentation:**
- See `docs/work-logs/` for detailed daily development activities
- See other phases in `docs/phases/`
