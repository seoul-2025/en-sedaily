# EventBridge Scheduler for Article Collection

# EventBridge Rule - Runs every 1 hour
resource "aws_cloudwatch_event_rule" "article_collection" {
  name                = "${var.project_name}-article-collection-${var.environment}"
  description         = "Trigger article collection every 1 hour"
  schedule_expression = "rate(1 hour)"
}

# Lambda Permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.article_collector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.article_collection.arn
}

# EventBridge Target - Article Collector Lambda
resource "aws_cloudwatch_event_target" "article_collector" {
  rule      = aws_cloudwatch_event_rule.article_collection.name
  target_id = "ArticleCollectorLambda"
  arn       = aws_lambda_function.article_collector.arn

  input = jsonencode({
    hours = 1
  })
}

# Article Collector Lambda Function
resource "aws_lambda_function" "article_collector" {
  function_name = "${var.project_name}-article-collector-${var.environment}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handlers.article_collector.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300 # 5 minutes
  memory_size   = 1024

  s3_bucket = aws_s3_bucket.lambda_packages.id
  s3_key    = "lambda_package.zip"

  environment {
    variables = {
      BIGKINDS_API_KEY        = var.bigkinds_api_key
      BIGKINDS_API_URL        = "https://tools.kinds.or.kr"
      REGION                  = var.aws_region
      BEDROCK_MODEL_ID        = var.bedrock_model_id
      LOG_LEVEL               = var.log_level
      DYNAMODB_TABLE_ARTICLES = "${var.project_name}-articles-${var.environment}"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy_attachment.lambda_translate,
    aws_iam_role_policy_attachment.lambda_dynamodb
  ]
}

# CloudWatch Log Group for Article Collector
resource "aws_cloudwatch_log_group" "article_collector" {
  name              = "/aws/lambda/${aws_lambda_function.article_collector.function_name}"
  retention_in_days = 7
}
