variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "seodaily-eng"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "en.sedaily.ai"
}

variable "domain_name_com" {
  description = "Secondary domain name"
  type        = string
  default     = "en.sedaily.com"
}

variable "zone_id" {
  description = "Route53 hosted zone ID for sedaily.ai"
  type        = string
  default     = "Z07543813V4FC5RK599U0"
}

variable "ssl_certificate_arn" {
  description = "ACM certificate ARN for *.sedaily.ai"
  type        = string
  default     = "arn:aws:acm:us-east-1:887078546492:certificate/ae647d30-3b86-429b-84b8-57398d536046"
}

variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

variable "ec2_ami_id" {
  description = "EC2 AMI ID (Amazon Linux 2)"
  type        = string
  default     = "ami-0c02fb55956c7d316"
}