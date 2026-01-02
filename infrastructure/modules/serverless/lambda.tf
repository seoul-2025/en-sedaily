# Lambda function for article management
resource "aws_lambda_function" "article" {
  filename         = "lambda-packages/article-handler.zip"
  function_name    = "${var.project_name}-article-${var.environment}"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "article_handler.lambda_handler"
  source_code_hash = fileexists("lambda-packages/article-handler.zip") ? filebase64sha256("lambda-packages/article-handler.zip") : ""
  runtime         = "python3.11"
  memory_size     = 1024
  timeout         = 30

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ENVIRONMENT        = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-article-function"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_dynamodb,
    aws_cloudwatch_log_group.article_lambda,
  ]
}

# Lambda function for search functionality
resource "aws_lambda_function" "search" {
  filename         = "lambda-packages/search-handler.zip"
  function_name    = "${var.project_name}-search-${var.environment}"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "search_handler.lambda_handler"
  source_code_hash = fileexists("lambda-packages/search-handler.zip") ? filebase64sha256("lambda-packages/search-handler.zip") : ""
  runtime         = "python3.11"
  memory_size     = 1024
  timeout         = 30

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ENVIRONMENT        = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-search-function"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_dynamodb,
    aws_cloudwatch_log_group.search_lambda,
  ]
}

# Lambda function for CMS update
resource "aws_lambda_function" "cms_update" {
  filename         = "lambda-packages/cms-update.zip"
  function_name    = "${var.project_name}-cms-update-${var.environment}"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "cms_update_handler.lambda_handler"
  source_code_hash = fileexists("lambda-packages/cms-update.zip") ? filebase64sha256("lambda-packages/cms-update.zip") : ""
  runtime         = "python3.11"
  memory_size     = 512
  timeout         = 30

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      ENVIRONMENT        = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-cms-update-function"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.lambda_dynamodb,
    aws_cloudwatch_log_group.cms_update_lambda,
  ]
}

# CloudWatch Log Groups for Lambda functions
resource "aws_cloudwatch_log_group" "article_lambda" {
  name              = "/aws/lambda/${var.project_name}-article-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-article-logs"
  }
}

resource "aws_cloudwatch_log_group" "collector_lambda" {
  name              = "/aws/lambda/${var.project_name}-article-collector-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-collector-logs"
  }
}

resource "aws_cloudwatch_log_group" "search_lambda" {
  name              = "/aws/lambda/${var.project_name}-search-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-search-logs"
  }
}

resource "aws_cloudwatch_log_group" "cms_update_lambda" {
  name              = "/aws/lambda/${var.project_name}-cms-update-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-cms-update-logs"
  }
}

resource "aws_cloudwatch_log_group" "cms_delete_lambda" {
  name              = "/aws/lambda/${var.project_name}-cms-delete-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-cms-delete-logs"
  }
}