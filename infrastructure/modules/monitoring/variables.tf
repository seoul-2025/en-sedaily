variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for monitoring"
  type        = string
  default     = ""
}

variable "api_gateway_id" {
  description = "API Gateway ID for monitoring"
  type        = string
  default     = ""
}

variable "ec2_instance_id" {
  description = "EC2 instance ID for monitoring"
  type        = string
  default     = ""
}

variable "lambda_function_names" {
  description = "List of Lambda function names to monitor"
  type        = list(string)
  default     = []
}

variable "alert_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}
