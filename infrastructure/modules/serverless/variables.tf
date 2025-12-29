variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for articles"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "DynamoDB table ARN for articles"
  type        = string
}