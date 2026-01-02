###############################################################################
# CloudWatch Logs Retention Settings
#
# Lambda 함수 로그를 30일간 보관 (비용 절감)
# 보관 기간이 없으면 로그가 무한정 쌓여 비용 증가
###############################################################################

# Lambda function log groups
locals {
  lambda_log_groups = [
    for func_name in var.lambda_function_names :
    "/aws/lambda/${func_name}"
  ]
}

# Set retention policy for Lambda logs
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count = length(local.lambda_log_groups)

  name              = local.lambda_log_groups[count.index]
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-lambda-logs"
    Environment = var.environment
    CostCenter  = "Monitoring"
  }
}

# Additional log groups (if needed)
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  count = var.api_gateway_id != "" ? 1 : 0

  name              = "/aws/apigateway/${var.project_name}-api-${var.environment}"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-api-gateway-logs"
    Environment = var.environment
    CostCenter  = "Monitoring"
  }
}
