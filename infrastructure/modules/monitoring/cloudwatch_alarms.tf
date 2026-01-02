###############################################################################
# CloudWatch Alarms for Seoul Economic Daily
#
# 대기업급 알람 시스템:
# - EC2 CPU 과부하 감지
# - API Gateway 에러율 증가 감지
# - Lambda 함수 실패 감지
# - CloudFront 5xx 에러 급증 감지
#
# 알림 방식: SNS → Email/SMS
###############################################################################

# SNS Topic for alarms
resource "aws_sns_topic" "alarms" {
  count = var.alert_email != "" ? 1 : 0
  name  = "${var.project_name}-cloudwatch-alarms"

  tags = {
    Name        = "${var.project_name}-alarms"
    Environment = var.environment
  }
}

# SNS Topic Subscription (Email)
resource "aws_sns_topic_subscription" "email_alert" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ============================================================================
# EC2 CPU High Utilization Alarm (서버 과부하)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  count               = var.ec2_instance_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-ec2-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "EC2 CPU 사용률이 80%를 초과했습니다. 서버 증설을 고려하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    InstanceId = var.ec2_instance_id
  }

  tags = {
    Name     = "${var.project_name}-ec2-cpu-alarm"
    Severity = "High"
  }
}

# ============================================================================
# EC2 Status Check Failed (서버 다운)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "ec2_status_check_failed" {
  count               = var.ec2_instance_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-ec2-status-check-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "EC2 인스턴스 상태 체크 실패! 즉시 확인이 필요합니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    InstanceId = var.ec2_instance_id
  }

  tags = {
    Name     = "${var.project_name}-ec2-status-alarm"
    Severity = "Critical"
  }
}

# ============================================================================
# API Gateway 5xx Error Rate High (백엔드 에러 급증)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  count               = var.api_gateway_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "API Gateway에서 5xx 에러가 10개 이상 발생했습니다. 백엔드를 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    ApiName = "${var.project_name}-api-${var.environment}"
  }

  tags = {
    Name     = "${var.project_name}-api-5xx-alarm"
    Severity = "High"
  }
}

# ============================================================================
# API Gateway High Latency (응답 지연)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "api_high_latency" {
  count               = var.api_gateway_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-api-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Average"
  threshold           = 3000
  alarm_description   = "API 평균 응답시간이 3초를 초과했습니다. 성능 최적화가 필요합니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    ApiName = "${var.project_name}-api-${var.environment}"
  }

  tags = {
    Name     = "${var.project_name}-api-latency-alarm"
    Severity = "Medium"
  }
}

# ============================================================================
# Lambda Error Rate High (서버리스 함수 에러)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count               = length(var.lambda_function_names) > 0 && var.alert_email != "" ? length(var.lambda_function_names) : 0
  alarm_name          = "${var.project_name}-lambda-${var.lambda_function_names[count.index]}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Lambda 함수 ${var.lambda_function_names[count.index]}에서 에러가 5개 이상 발생했습니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    FunctionName = var.lambda_function_names[count.index]
  }

  tags = {
    Name     = "${var.project_name}-lambda-${var.lambda_function_names[count.index]}-alarm"
    Severity = "Medium"
  }
}

# ============================================================================
# CloudFront 5xx Error Rate High (CDN 에러)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "cloudfront_5xx_errors" {
  count               = var.cloudfront_distribution_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-cloudfront-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 5
  alarm_description   = "CloudFront 5xx 에러율이 5%를 초과했습니다. Origin 서버를 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    DistributionId = var.cloudfront_distribution_id
  }

  tags = {
    Name     = "${var.project_name}-cloudfront-5xx-alarm"
    Severity = "High"
  }
}

# ============================================================================
# CloudFront Cache Hit Rate Low (캐시 효율 저하)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "cloudfront_cache_hit_low" {
  count               = var.cloudfront_distribution_id != "" && var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-cloudfront-cache-hit-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CacheHitRate"
  namespace           = "AWS/CloudFront"
  period              = 300
  statistic           = "Average"
  threshold           = 50
  alarm_description   = "CloudFront 캐시 적중률이 50% 미만입니다. 캐시 설정을 확인하세요."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    DistributionId = var.cloudfront_distribution_id
  }

  tags = {
    Name     = "${var.project_name}-cloudfront-cache-alarm"
    Severity = "Low"
  }
}

# ============================================================================
# AWS Cost Budget Alarm (비용 초과)
# ============================================================================
resource "aws_cloudwatch_metric_alarm" "estimated_charges" {
  count               = var.alert_email != "" ? 1 : 0
  alarm_name          = "${var.project_name}-estimated-charges-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400
  statistic           = "Maximum"
  threshold           = 100
  alarm_description   = "AWS 월별 예상 비용이 $100를 초과했습니다."
  alarm_actions       = [aws_sns_topic.alarms[0].arn]

  dimensions = {
    Currency = "USD"
  }

  tags = {
    Name     = "${var.project_name}-cost-alarm"
    Severity = "Medium"
  }
}

# Output alarm ARNs
output "alarm_arns" {
  description = "ARNs of all CloudWatch alarms"
  value = merge(
    var.ec2_instance_id != "" && var.alert_email != "" ? {
      ec2_cpu_high           = try(aws_cloudwatch_metric_alarm.ec2_cpu_high[0].arn, "")
      ec2_status_check       = try(aws_cloudwatch_metric_alarm.ec2_status_check_failed[0].arn, "")
    } : {},
    var.api_gateway_id != "" && var.alert_email != "" ? {
      api_5xx_errors         = try(aws_cloudwatch_metric_alarm.api_5xx_errors[0].arn, "")
      api_high_latency       = try(aws_cloudwatch_metric_alarm.api_high_latency[0].arn, "")
    } : {},
    var.cloudfront_distribution_id != "" && var.alert_email != "" ? {
      cloudfront_5xx_errors  = try(aws_cloudwatch_metric_alarm.cloudfront_5xx_errors[0].arn, "")
      cloudfront_cache_hit   = try(aws_cloudwatch_metric_alarm.cloudfront_cache_hit_low[0].arn, "")
    } : {},
    var.alert_email != "" ? {
      estimated_charges      = try(aws_cloudwatch_metric_alarm.estimated_charges[0].arn, "")
    } : {}
  )
}
