# AWS Infrastructure Audit - English Sedaily Project

**Date:** 2025-12-16  
**Account:** 887078546492  
**Region:** us-east-1 (primary)  
**Purpose:** Comprehensive infrastructure documentation for Terraform management

## Current Production Environment

### 1. EC2 Infrastructure

#### Main Application Server
- **Instance ID:** i-05298ffc0455ee5ce
- **Type:** t3.small
- **Public IP:** 52.21.195.0
- **State:** running
- **Security Group:** sg-0bb3e61c52c16d0be (sedaily-eng-sg-1765859670)
- **Key Pair:** sedaily-eng-key
- **Purpose:** Next.js SSR application hosting

### 2. Domain & DNS Configuration

#### Primary Domains
- **en.sedaily.ai** (CNAME → d39c7rf2w6v6qi.cloudfront.net)
- **en.sedaily.com** (Alias for en.sedaily.ai)

#### Route53 Hosted Zones
- **sedaily.ai** (Zone ID: Z07543813V4FC5RK599U0) - 50 records
- **sedaily.io** (Zone ID: Z0004464118K81FTONS25) - 24 records

### 3. CloudFront Distribution

#### Main Distribution (EUWQ1K71CXJUH)
```yaml
Distribution ID: EUWQ1K71CXJUH
Domain: d39c7rf2w6v6qi.cloudfront.net
Aliases:
  - en.sedaily.ai
  - en.sedaily.com
Comment: "Seoul Economic Daily - EC2 SSR"
Origin:
  Domain: origin-en.sedaily.ai
  Protocol: HTTP-only
  Port: 80
  Read Timeout: 30s
  Keep-alive: 5s
```

### 4. Lambda Functions (English Project)

#### Core API Functions
```yaml
seodaily-eng-article-dev:
  Memory: 1024MB
  Runtime: python3.11
  Timeout: 30s
  Role: seodaily-eng-lambda-execution-dev

seodaily-eng-article-collector-dev:
  Memory: 1024MB
  Runtime: python3.11
  Timeout: 300s
  Role: seodaily-eng-lambda-execution-dev

seodaily-eng-search-dev:
  Memory: 1024MB
  Runtime: python3.11
  Timeout: 30s
  Role: seodaily-eng-lambda-execution-dev
```

#### CMS Functions (Currently Active)
```yaml
seodaily-eng-cms-update-dev:
  Memory: 512MB
  Runtime: python3.11
  Timeout: 30s
  Role: seodaily-eng-lambda-execution-dev

seodaily-eng-cms-delete-dev:
  Memory: 512MB
  Runtime: python3.11
  Timeout: 30s
  Role: seodaily-eng-lambda-execution-dev
```

#### Admin API Functions (Disabled per CMS_CONSOLIDATION.md)
```yaml
seodaily-eng-admin-delete-dev:
  Memory: 512MB
  Status: UNUSED (admin.tf.unused)

seodaily-eng-admin-get-dev:
  Memory: 512MB
  Status: UNUSED (admin.tf.unused)

seodaily-eng-admin-update-dev:
  Memory: 512MB
  Status: UNUSED (admin.tf.unused)

seodaily-eng-admin-bulk-dev:
  Memory: 512MB
  Status: UNUSED (admin.tf.unused)

seodaily-eng-admin-list-dev:
  Memory: 512MB
  Status: UNUSED (admin.tf.unused)
```

### 5. API Gateway

#### Main API (7w5nco7xn4)
- **Name:** seodaily-eng-api-dev
- **ID:** 7w5nco7xn4
- **Created:** 2025-11-28
- **Endpoint:** https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
- **Purpose:** Backend API for article management and content delivery

### 6. S3 Buckets (English Project Related)

#### Active Buckets
- **sedaily-ai-frontend** (2025-09-13) - Main frontend assets
- **sedaily-ai-web** (2025-09-10) - Web assets
- **sedaily-ai-nova** (2025-09-20) - AI Nova integration
- **sedaily-io** (2025-08-03) - Legacy assets

#### CMS Buckets  
- **enadmin.sedaily.ai** related buckets for CMS frontend

### 7. Current vs Terraform State

#### Terraform Managed Resources
Based on existing .tf files in infrastructure/:
- ✅ CloudFront distribution (main.tf)
- ✅ Route53 records (route53.tf)  
- ✅ Lambda functions (lambda.tf)
- ✅ API Gateway (api_gateway.tf)
- ✅ S3 buckets (s3.tf)
- ✅ IAM roles (iam.tf)

#### Manual/Legacy Resources
- ❌ EC2 instance (i-05298ffc0455ee5ce) - **NOT IN TERRAFORM**
- ❌ Security groups (sg-0bb3e61c52c16d0be) - **NOT IN TERRAFORM**  
- ❌ Key pairs (sedaily-eng-key) - **NOT IN TERRAFORM**

### 8. Infrastructure Gap Analysis

#### Missing from Terraform
1. **EC2 Infrastructure**
   - Instance: i-05298ffc0455ee5ce (t3.small)
   - Security Group: sg-0bb3e61c52c16d0b   
   - Key Pair: sedaily-eng-key

2. **Load Balancer/ALB**
   - No ALB found - direct CloudFront → EC2 setup

3. **Auto Scaling**
   - No ASG configured - single EC2 instance

#### Terraform Configuration Required
```hcl
# ec2.tf - NEEDS TO BE CREATED
resource "aws_instance" "sedaily_eng_web" {
  ami                    = "ami-0c02fb55956c7d316" # Amazon Linux 2
  instance_type          = "t3.small"
  key_name              = aws_key_pair.sedaily_eng.key_name
  security_groups       = [aws_security_group.sedaily_eng.name]
  
  tags = {
    Name = "sedaily-eng-web"
    Environment = "production"
  }
}

resource "aws_security_group" "sedaily_eng" {
  name = "sedaily-eng-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443  
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Restrict as needed
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "sedaily_eng" {
  key_name   = "sedaily-eng-key"
  public_key = file("~/.ssh/sedaily-eng-key.pub") # Needs public key
}
```

### 9. Deployment Pipeline

#### Current Process
- **Source:** `/Users/yeong-gwang/Documents/work/서울경제신문/DEV/영문사이트/en-sedaily-1st-main/frontend`
- **Build:** Next.js standalone build
- **Deploy:** `deploy.sh` script → SCP to EC2 → PM2 restart
- **PM2 App:** sedaily-eng (port 3000)

#### Architecture Flow
```
Internet → CloudFront (EUWQ1K71CXJUH) → EC2 (52.21.195.0:3000) → PM2 → Next.js App
                                      ↓
                                API Gateway (7w5nco7xn4) → Lambda Functions
```

### 10. Security & Access

#### IAM Roles in Use
- **seodaily-eng-lambda-execution-dev** (Lambda functions)
- **sedaily-eng-sg-1765859670** (EC2 security group)

#### SSL/TLS
- CloudFront handles SSL termination
- EC2 serves HTTP only (port 80)

### 11. Monitoring & Logging

#### Current Setup
- PM2 process management on EC2
- CloudWatch logs (Lambda functions)
- CloudFront access logs (if enabled)

#### Gaps
- No EC2 monitoring in CloudWatch
- No application-level health checks
- No automated backup strategy for EC2

### 12. Recommendations for Terraform Migration

#### Phase 1: Import Existing Resources
```bash
terraform import aws_instance.sedaily_eng_web i-05298ffc0455ee5ce
terraform import aws_security_group.sedaily_eng sg-0bb3e61c52c16d0be
```

#### Phase 2: Infrastructure Improvements
- Add Application Load Balancer
- Implement Auto Scaling Group
- Add CloudWatch monitoring
- Setup automated backups
- Implement blue/green deployments

#### Phase 3: CI/CD Pipeline
- GitHub Actions integration
- Automated testing
- Infrastructure as Code validation

---

**Last Updated:** 2025-12-16  
**Next Actions:** Create ec2.tf and import existing resources into Terraform state