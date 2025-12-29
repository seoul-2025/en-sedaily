# CMS Delete Article Lambda and API Gateway

# Lambda Function for CMS Delete
resource "aws_lambda_function" "cms_delete" {
  function_name = "seodaily-eng-cms-delete-dev"
  handler       = "handlers.cms_delete_handler.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_execution.arn
  timeout       = 30
  memory_size   = 512

  s3_bucket = "seodaily-eng-lambda-packages-dev"
  s3_key    = "lambda-admin.zip"

  environment {
    variables = {
      DYNAMODB_TABLE_ARTICLES = "seodaily-eng-articles-dev"
    }
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "cms_delete" {
  name              = "/aws/lambda/seodaily-eng-cms-delete-dev"
  retention_in_days = 7
}

# API Gateway Resource: /api/delete-article
resource "aws_api_gateway_resource" "delete_article" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "delete-article"
}

# POST /api/delete-article
resource "aws_api_gateway_method" "delete_article_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.delete_article.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "delete_article_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.delete_article.id
  http_method             = aws_api_gateway_method.delete_article_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.cms_delete.invoke_arn
}

resource "aws_lambda_permission" "delete_article_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cms_delete.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# OPTIONS /api/delete-article (CORS)
resource "aws_api_gateway_method" "delete_article_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.delete_article.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "delete_article_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.delete_article.id
  http_method = aws_api_gateway_method.delete_article_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "delete_article_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.delete_article.id
  http_method = aws_api_gateway_method.delete_article_options.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "delete_article_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.delete_article.id
  http_method = aws_api_gateway_method.delete_article_options.http_method
  status_code = aws_api_gateway_method_response.delete_article_options.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}
