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

variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

variable "domain_name_com" {
  description = "Secondary domain name (.com)"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "ssl_certificate_arn" {
  description = "ACM certificate ARN"
  type        = string
}

variable "ec2_public_ip" {
  description = "Public IP of EC2 instance"
  type        = string
}