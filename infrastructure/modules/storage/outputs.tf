output "articles_table_name" {
  description = "Articles DynamoDB table name"
  value       = aws_dynamodb_table.articles.name
}

output "articles_table_arn" {
  description = "Articles DynamoDB table ARN"
  value       = aws_dynamodb_table.articles.arn
}