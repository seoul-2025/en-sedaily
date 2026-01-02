output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.main.id
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "https://${aws_api_gateway_rest_api.main.id}.execute-api.${var.region}.amazonaws.com/${var.environment}"
}

output "cms_url" {
  description = "CMS Admin URL"
  value       = "https://enadmin.sedaily.ai"
}

output "cms_cloudfront_domain" {
  description = "CMS CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.cms.domain_name
}

output "lambda_article_function_name" {
  description = "Name of the article Lambda function"
  value       = aws_lambda_function.article.function_name
}