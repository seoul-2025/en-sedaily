# Main Terraform configuration for Seoul Economic Daily English site
# Development Environment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure for remote state management
  # backend "s3" {
  #   bucket  = "seodaily-eng-terraform-state"
  #   key     = "dev/terraform.tfstate"
  #   region  = "us-east-1"
  # }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Compute Infrastructure
module "compute" {
  source = "../../modules/compute"

  project_name      = var.project_name
  environment       = var.environment
  region           = var.region
  instance_type    = var.ec2_instance_type
  ami_id          = var.ec2_ami_id
  key_name        = "${var.project_name}-key"
}

# Networking Infrastructure
module "networking" {
  source = "../../modules/networking"

  project_name         = var.project_name
  environment          = var.environment
  region              = var.region
  domain_name         = var.domain_name
  domain_name_com     = var.domain_name_com
  zone_id             = var.zone_id
  ssl_certificate_arn = var.ssl_certificate_arn
  
  # Dependencies
  ec2_public_ip = module.compute.ec2_public_ip
}

# Storage Infrastructure
module "storage" {
  source = "../../modules/storage"

  project_name = var.project_name
  environment  = var.environment
  region      = var.region
}

# Serverless Infrastructure
module "serverless" {
  source = "../../modules/serverless"

  project_name = var.project_name
  environment  = var.environment
  region      = var.region
  
  # Dependencies
  dynamodb_table_name = module.storage.articles_table_name
  dynamodb_table_arn  = module.storage.articles_table_arn
}

# Outputs
output "website_url" {
  description = "Main website URL"
  value       = "https://${var.domain_name}"
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = module.serverless.api_gateway_url
}

output "cms_url" {
  description = "CMS Admin URL"
  value       = module.serverless.cms_url
}

output "ec2_public_ip" {
  description = "EC2 Public IP"
  value       = module.compute.ec2_public_ip
}

output "cloudfront_distribution_id" {
  description = "CloudFront Distribution ID"
  value       = module.networking.cloudfront_distribution_id
}