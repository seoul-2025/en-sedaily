# Related Articles Lambda Function and API Gateway Integration
# Provides hashtag-based article recommendations

# Lambda function for related articles
resource "aws_lambda_function" "related_articles_handler" {
  filename         = "related_articles_handler.zip"
  function_name    = "${var.project_name}-related-articles-${var.environment}"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "handlers.related_articles_handler.lambda_handler"
  source_code_hash = fileexists("related_articles_handler.zip") ? filebase64sha256("related_articles_handler.zip") : ""
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = var.log_level
    }
  }

  tags = {
    Name        = "${var.project_name}-related-articles-handler"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "related_articles_handler_logs" {
  name              = "/aws/lambda/${aws_lambda_function.related_articles_handler.function_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-related-articles-logs"
    Environment = var.environment
  }
}

# API Gateway resource for /api/related
resource "aws_api_gateway_resource" "related" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "related"
}

# API Gateway resource for /api/related/{article_id}
resource "aws_api_gateway_resource" "related_article_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.related.id
  path_part   = "{article_id}"
}

# API Gateway GET method for /api/related/{article_id}
resource "aws_api_gateway_method" "related_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.related_article_id.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.article_id" = true
  }
}

# API Gateway integration for related articles
resource "aws_api_gateway_integration" "related_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.related_article_id.id
  http_method             = aws_api_gateway_method.related_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.related_articles_handler.invoke_arn
}

# CORS configuration for /api/related/{article_id}
resource "aws_api_gateway_method" "related_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.related_article_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "related_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.related_article_id.id
  http_method = aws_api_gateway_method.related_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "related_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.related_article_id.id
  http_method = aws_api_gateway_method.related_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "related_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.related_article_id.id
  http_method = aws_api_gateway_method.related_options.http_method
  status_code = aws_api_gateway_method_response.related_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "related_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.related_articles_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# Output
output "related_articles_lambda_arn" {
  description = "Related Articles Lambda function ARN"
  value       = aws_lambda_function.related_articles_handler.arn
}
