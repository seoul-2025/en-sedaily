# Seoul Economic Daily - English Site Infrastructure

This directory contains Terraform configurations for managing the AWS infrastructure of the English Seoul Economic Daily website, organized into modular and reusable components.

## 📁 Directory Structure

```
infrastructure/
├── README.md                    # This documentation
├── AWS_INFRASTRUCTURE_AUDIT.md  # Current AWS resources audit
├── CMS_CONSOLIDATION.md         # CMS consolidation documentation
│
├── environments/                # Environment-specific configurations
│   └── dev/                    # Development environment
│       ├── main.tf             # Main configuration calling modules
│       ├── providers.tf        # Provider configuration
│       ├── variables.tf        # Environment variables
│       └── terraform.tfvars.example  # Example variables
│
├── modules/                     # Reusable Terraform modules
│   ├── compute/                # EC2 infrastructure
│   │   ├── ec2.tf             # EC2, Security Groups, Key Pairs
│   │   ├── variables.tf       # Module variables
│   │   └── outputs.tf         # Module outputs
│   │
│   ├── networking/            # CloudFront, Route53, DNS
│   │   ├── cloudfront.tf      # CloudFront distribution
│   │   ├── route53.tf         # DNS records
│   │   ├── variables.tf       # Module variables
│   │   └── outputs.tf         # Module outputs
│   │
│   ├── storage/               # DynamoDB, S3 storage
│   │   ├── dynamodb_articles.tf  # Article database
│   │   ├── variables.tf       # Module variables
│   │   └── outputs.tf         # Module outputs
│   │
│   └── serverless/            # Lambda, API Gateway, CMS
│       ├── lambda.tf          # Lambda functions
│       ├── api_gateway.tf     # API Gateway configuration
│       ├── iam.tf             # IAM roles and policies
│       ├── cms.tf             # CMS infrastructure
│       ├── cms_delete.tf      # CMS delete functionality
│       ├── route53_cms.tf     # CMS DNS records
│       ├── variables.tf       # Module variables
│       └── outputs.tf         # Module outputs
│
├── shared/                      # Shared resources (future use)
├── keys/                        # SSH keys directory (create manually)
├── lambda-packages/             # Lambda deployment packages (create manually)
│
└── legacy/                     # Legacy files (move here if needed)
    ├── related_articles.tf    # Related articles functionality
    ├── eventbridge.tf         # Event-driven automation
    └── admin.tf.unused        # Disabled admin API
```

## 🏗 Architecture Overview

```
Internet → CloudFront → EC2 (Next.js SSR) → API Gateway → Lambda Functions → DynamoDB
           (HTTPS)       (PM2/Node.js)        (REST API)    (Python)      (Articles)
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
cd environments/dev
cp terraform.tfvars.example terraform.tfvars
```

### 2. Configure Variables

Edit `terraform.tfvars`:

```hcl
project_name = "seodaily-eng"
environment  = "dev"
region      = "us-east-1"
domain_name = "en.sedaily.ai"
domain_name_com = "en.sedaily.com"
zone_id     = "Z07543813V4FC5RK599U0"
ssl_certificate_arn = "arn:aws:acm:us-east-1:887078546492:certificate/ae647d30-3b86-429b-84b8-57398d536046"
```

### 3. Prepare Required Files

```bash
# Create SSH key directory
mkdir -p ../../keys/
# Add your public SSH key
cp ~/.ssh/your-key.pub ../../keys/sedaily-eng-key.pub

# Create Lambda packages directory
mkdir -p ../../lambda-packages/
# Add your Lambda deployment packages
```

### 4. Initialize and Deploy

```bash
terraform init
terraform plan
terraform apply
```

## 📦 Modules Overview

### Compute Module (`modules/compute/`)

**Purpose**: EC2 infrastructure for web server hosting

- **Resources**: EC2 instance, Security Groups, Elastic IP, Key Pairs
- **Outputs**: Instance ID, Public IP, Private IP, Security Group ID

### Networking Module (`modules/networking/`)

**Purpose**: CDN, DNS, and routing infrastructure

- **Resources**: CloudFront distribution, Route53 records
- **Outputs**: CloudFront domain, Distribution ID, DNS records

### Storage Module (`modules/storage/`)

**Purpose**: Data persistence and storage

- **Resources**: DynamoDB tables with GSI for articles
- **Outputs**: Table names and ARNs

### Serverless Module (`modules/serverless/`)

**Purpose**: API, Lambda functions, and CMS infrastructure

- **Resources**: Lambda functions, API Gateway, IAM roles, CMS CloudFront
- **Outputs**: API endpoints, function names, CMS URL

## 🔧 Module Usage Examples

### Using Individual Modules

```hcl
# Use only compute module for testing
module "compute_only" {
  source = "../../modules/compute"

  project_name  = "test-project"
  environment   = "dev"
  region       = "us-east-1"
  instance_type = "t3.micro"
  ami_id       = "ami-0c02fb55956c7d316"
  key_name     = "test-key"
}
```

### Environment-Specific Configurations

```hcl
# Production environment with different settings
module "compute" {
  source = "../../modules/compute"

  project_name  = var.project_name
  environment   = "prod"
  instance_type = "t3.medium"  # Larger instance for production
  ami_id       = var.ami_id
  key_name     = "${var.project_name}-prod-key"
}
```

## 🔄 Deployment Workflow

### Development Workflow

1. **Make changes** in appropriate module
2. **Test locally** with `terraform plan`
3. **Apply changes** with `terraform apply`
4. **Validate** infrastructure changes

### Production Deployment

1. **Environment promotion**: dev → staging → prod
2. **State management**: Use remote state for production
3. **Change management**: Review process for infrastructure changes

## 🔒 Security Considerations

### Module Security

- **IAM**: Principle of least privilege in serverless module
- **Network**: Security groups restrict access in compute module
- **SSL/TLS**: Certificate management in networking module

### Secrets Management

- Store sensitive variables in AWS Secrets Manager
- Use Terraform variables for non-sensitive configuration
- Never commit secrets to version control

## 🔍 Import Existing Resources

If you have existing AWS resources, import them before running apply:

```bash
# Navigate to dev environment
cd environments/dev

# Import existing resources
terraform import module.compute.aws_instance.web_server i-05298ffc0455ee5ce
terraform import module.compute.aws_security_group.web_server sg-0bb3e61c52c16d0be
terraform import module.networking.aws_cloudfront_distribution.main EUWQ1K71CXJUH
```

## 🔧 Common Operations

### Add New Environment

```bash
# Create new environment directory
cp -r environments/dev environments/staging

# Update variables for staging
vim environments/staging/terraform.tfvars

# Update backend configuration if using remote state
vim environments/staging/providers.tf
```

### Create Custom Module

```bash
# Create new module directory
mkdir modules/monitoring

# Add module files
touch modules/monitoring/{main.tf,variables.tf,outputs.tf}
```

### Update Lambda Functions

```bash
# Update Lambda package
zip -r lambda-packages/new-function.zip src/

# Update module reference
vim modules/serverless/lambda.tf

# Apply changes
terraform apply
```

## 🏷 Naming Conventions

### Resources

- **Pattern**: `{project}-{resource}-{environment}`
- **Example**: `seodaily-eng-web-server-dev`

### Variables

- **Snake case**: `project_name`, `instance_type`
- **Descriptive**: `ssl_certificate_arn` not `cert_arn`

### Modules

- **Descriptive directories**: `compute`, `networking`, `storage`
- **Clear boundaries**: Each module has single responsibility

## 🔧 Troubleshooting

### Module Issues

```bash
# Check module source paths
terraform get -update

# Validate module syntax
terraform validate

# Check specific module plan
terraform plan -target=module.compute
```

### Dependency Issues

```bash
# Refresh state
terraform refresh

# Check resource dependencies
terraform graph | dot -Tpng > graph.png
```

### State Management

```bash
# List all resources
terraform state list

# Show specific resource
terraform state show module.compute.aws_instance.web_server

# Move resource between modules
terraform state mv aws_instance.old module.compute.aws_instance.web_server
```

## 📊 Outputs

After successful deployment, you'll get:

```
website_url = "https://en.sedaily.ai"
api_gateway_url = "https://xyz123.execute-api.us-east-1.amazonaws.com/dev"
cms_url = "https://enadmin.sedaily.ai"
ec2_public_ip = "52.21.195.0"
cloudfront_distribution_id = "EUWQ1K71CXJUH"
```

## 📈 Monitoring

### CloudWatch Integration

- Lambda function logs in serverless module
- EC2 monitoring in compute module
- CloudFront metrics in networking module

### Cost Optimization

- Instance type variables for easy scaling
- On-demand vs reserved instance configuration
- Lambda memory optimization

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Infrastructure
on:
  push:
    paths: ["infrastructure/**"]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: hashicorp/setup-terraform@v2
      - run: terraform init
        working-directory: infrastructure/environments/dev
      - run: terraform apply -auto-approve
        working-directory: infrastructure/environments/dev
```

---

**Last Updated**: 2025-12-16  
**Terraform Version**: >= 1.0  
**AWS Provider**: ~> 5.0  
**Module Structure**: Organized for reusability and maintainability
