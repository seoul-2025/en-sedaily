# DynamoDB table for articles with GSI for efficient queries
resource "aws_dynamodb_table" "articles" {
  name         = "${var.project_name}-articles-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "news_id"

  attribute {
    name = "news_id"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  attribute {
    name = "published_at"
    type = "S"
  }

  # GSI for category + date queries (improves search performance)
  global_secondary_index {
    name            = "category-published_at-index"
    hash_key        = "category"
    range_key       = "published_at"
    projection_type = "ALL"
  }

  # Point-in-time recovery for backup (데이터 유실 방지)
  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-articles"
    Environment = var.environment
  }
}

