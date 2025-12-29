#!/bin/bash
# Quick Deployment Script for SEOdaily-ENG
# This script automates the entire deployment process

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

print_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_error() {
    echo -e "${RED}✗ ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ SUCCESS:${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_tools=()
    
    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi
    
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws")
    fi
    
    if ! command -v node &> /dev/null; then
        missing_tools+=("node")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        echo "Please install missing tools and try again."
        exit 1
    fi
    
    print_success "All required tools are installed"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured"
        echo "Run 'aws configure' to set up your credentials"
        exit 1
    fi
    
    print_success "AWS credentials configured"
    
    # Check terraform.tfvars exists
    if [ ! -f "$SCRIPT_DIR/terraform.tfvars" ]; then
        print_error "terraform.tfvars not found"
        echo "Please create terraform.tfvars from terraform.tfvars.example"
        exit 1
    fi
    
    print_success "terraform.tfvars found"
}

# Build Lambda packages
build_lambda_packages() {
    print_header "Building Lambda Packages"
    
    cd "$SCRIPT_DIR"
    
    if [ ! -f "deploy.sh" ]; then
        print_error "deploy.sh not found"
        exit 1
    fi
    
    chmod +x deploy.sh
    
    print_step "Running deploy.sh to package Lambda functions..."
    if ./deploy.sh; then
        print_success "Lambda packages built successfully"
    else
        print_error "Failed to build Lambda packages"
        exit 1
    fi
    
    # Verify packages exist
    if [ ! -f "search_handler.zip" ] || [ ! -f "article_handler.zip" ]; then
        print_error "Lambda package files not found"
        exit 1
    fi
    
    print_success "Lambda packages verified"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    print_header "Deploying Infrastructure with Terraform"
    
    cd "$SCRIPT_DIR"
    
    print_step "Initializing Terraform..."
    if terraform init; then
        print_success "Terraform initialized"
    else
        print_error "Terraform init failed"
        exit 1
    fi
    
    print_step "Planning Terraform deployment..."
    if terraform plan -out=tfplan; then
        print_success "Terraform plan created"
    else
        print_error "Terraform plan failed"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}Review the plan above. Do you want to proceed with deployment?${NC}"
    read -p "Type 'yes' to continue: " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_warning "Deployment cancelled by user"
        exit 0
    fi
    
    print_step "Applying Terraform configuration..."
    if terraform apply tfplan; then
        print_success "Infrastructure deployed successfully"
    else
        print_error "Terraform apply failed"
        exit 1
    fi
    
    # Save outputs
    print_step "Saving Terraform outputs..."
    terraform output > deployment_outputs.txt
    print_success "Outputs saved to deployment_outputs.txt"
}

# Build and deploy frontend
deploy_frontend() {
    print_header "Building and Deploying Frontend"
    
    # Get S3 bucket name and API URL from Terraform
    cd "$SCRIPT_DIR"
    S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null)
    API_URL=$(terraform output -raw api_gateway_url 2>/dev/null)
    
    if [ -z "$S3_BUCKET" ] || [ -z "$API_URL" ]; then
        print_error "Could not get Terraform outputs"
        exit 1
    fi
    
    print_step "S3 Bucket: $S3_BUCKET"
    print_step "API URL: $API_URL"
    
    cd "$FRONTEND_DIR"
    
    # Create .env.production
    print_step "Creating .env.production..."
    echo "NEXT_PUBLIC_API_URL=$API_URL" > .env.production
    print_success ".env.production created"
    
    # Install dependencies
    print_step "Installing frontend dependencies..."
    if npm install; then
        print_success "Dependencies installed"
    else
        print_error "npm install failed"
        exit 1
    fi
    
    # Build frontend
    print_step "Building frontend..."
    if npm run build; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed"
        exit 1
    fi
    
    # Deploy to S3
    print_step "Deploying to S3..."
    if aws s3 sync out/ "s3://$S3_BUCKET" --delete; then
        print_success "Frontend deployed to S3"
    else
        print_error "S3 sync failed"
        exit 1
    fi
    
    # Invalidate CloudFront cache
    print_step "Getting CloudFront distribution ID..."
    DISTRIBUTION_ID=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?Comment=='seodaily-eng-cdn-dev'].Id" \
        --output text 2>/dev/null)
    
    if [ -n "$DISTRIBUTION_ID" ]; then
        print_step "Invalidating CloudFront cache..."
        if aws cloudfront create-invalidation \
            --distribution-id "$DISTRIBUTION_ID" \
            --paths "/*" > /dev/null; then
            print_success "CloudFront cache invalidated"
        else
            print_warning "CloudFront invalidation failed (non-critical)"
        fi
    else
        print_warning "Could not find CloudFront distribution (skipping invalidation)"
    fi
}

# Run deployment tests
run_tests() {
    print_header "Running Deployment Tests"
    
    cd "$SCRIPT_DIR"
    
    API_URL=$(terraform output -raw api_gateway_url 2>/dev/null)
    CLOUDFRONT_URL=$(terraform output -raw cloudfront_domain 2>/dev/null)
    
    if [ -z "$API_URL" ]; then
        print_error "Could not get API Gateway URL"
        exit 1
    fi
    
    print_step "API URL: $API_URL"
    if [ -n "$CLOUDFRONT_URL" ]; then
        print_step "CloudFront URL: https://$CLOUDFRONT_URL"
    fi
    
    if [ ! -f "test_deployment.sh" ]; then
        print_warning "test_deployment.sh not found, skipping tests"
        return
    fi
    
    chmod +x test_deployment.sh
    
    print_step "Running automated tests..."
    if API_GATEWAY_URL="$API_URL" CLOUDFRONT_DOMAIN="https://$CLOUDFRONT_URL" ./test_deployment.sh; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed. Review the output above."
    fi
}

# Print deployment summary
print_summary() {
    print_header "Deployment Summary"
    
    cd "$SCRIPT_DIR"
    
    API_URL=$(terraform output -raw api_gateway_url 2>/dev/null)
    CLOUDFRONT_URL=$(terraform output -raw cloudfront_domain 2>/dev/null)
    S3_BUCKET=$(terraform output -raw s3_bucket_name 2>/dev/null)
    
    echo ""
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo ""
    echo "Access your application:"
    echo -e "  Frontend: ${BLUE}https://$CLOUDFRONT_URL${NC}"
    echo -e "  API: ${BLUE}$API_URL${NC}"
    echo ""
    echo "Resources created:"
    echo "  S3 Bucket: $S3_BUCKET"
    echo "  CloudFront Distribution: $CLOUDFRONT_URL"
    echo "  API Gateway: $API_URL"
    echo ""
    echo "Next steps:"
    echo "  1. Open https://$CLOUDFRONT_URL in your browser"
    echo "  2. Test the search functionality"
    echo "  3. Review CloudWatch logs in AWS Console"
    echo "  4. Set up CloudWatch alarm notifications"
    echo ""
    echo "For detailed outputs, see: deployment_outputs.txt"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════╗"
    echo "║   SEOdaily-ENG Quick Deployment       ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_prerequisites
    build_lambda_packages
    deploy_infrastructure
    deploy_frontend
    run_tests
    print_summary
}

# Handle script interruption
trap 'echo -e "\n${RED}Deployment interrupted${NC}"; exit 1' INT TERM

# Run main
main
