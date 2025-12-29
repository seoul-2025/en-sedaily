# Technology Stack

## Programming Languages

### Backend
- **Python 3.11**: Primary backend language
- **Shell Script**: Build and deployment automation

### Frontend
- **TypeScript 5.3.0**: Type-safe React development
- **JavaScript**: Next.js configuration files

### Infrastructure
- **HCL (HashiCorp Configuration Language)**: Terraform IaC

## Backend Technologies

### Core Framework
- **FastAPI 0.115.0**: Modern async web framework
- **Uvicorn 0.32.0**: ASGI server with standard extras
- **Pydantic 2.10.0**: Data validation and settings management
- **Pydantic Settings 2.6.0**: Environment-based configuration

### HTTP Clients
- **httpx 0.27.0**: Async HTTP client for Anthropic API
- **aiohttp 3.9.1**: Alternative async HTTP client

### AWS SDK
- **boto3 1.35.0**: AWS SDK for Python
  - Lambda function invocation
  - DynamoDB operations
  - S3 file operations
  - CloudWatch logging

### Testing
- **pytest 8.3.0**: Testing framework
- **pytest-asyncio 0.24.0**: Async test support
- **hypothesis 6.122.0**: Property-based testing

### Utilities
- **python-dotenv 1.0.1**: Environment variable management
- **redis 5.2.0**: Caching layer (optional)

## Frontend Technologies

### Core Framework
- **Next.js 14.2.0**: React framework with App Router
- **React 18.3.0**: UI library
- **React DOM 18.3.0**: React rendering

### Styling
- **Tailwind CSS 3.4.0**: Utility-first CSS framework
- **PostCSS 8.4.0**: CSS transformation
- **Autoprefixer 10.4.0**: CSS vendor prefixing

### UI Components
- **Lucide React 0.344.0**: Icon library

### Development Tools
- **TypeScript 5.3.0**: Static type checking
- **ESLint 8.56.0**: Code linting
- **eslint-config-next 14.2.0**: Next.js ESLint configuration

### Type Definitions
- **@types/node 20.11.0**: Node.js type definitions
- **@types/react 18.2.0**: React type definitions
- **@types/react-dom 18.2.0**: React DOM type definitions

## Infrastructure Technologies

### Infrastructure as Code
- **Terraform**: AWS resource provisioning
- **AWS Provider**: Terraform AWS integration

### AWS Services
- **Lambda**: Serverless compute (Python 3.11 runtime)
- **API Gateway**: REST API management
- **DynamoDB**: NoSQL database
- **S3**: Static file storage
- **CloudFront**: CDN distribution
- **EventBridge**: Scheduled event triggers
- **CloudWatch**: Logging and monitoring
- **IAM**: Access management
- **ACM**: SSL certificate management
- **Route 53**: DNS management

### External APIs
- **BigKinds API**: Korean news article source
- **Anthropic Claude API**: AI translation service
  - Model: claude-opus-4-5-20251101
  - Endpoint: https://api.anthropic.com/v1/messages

## Development Commands

### Backend Development

```bash
# Setup virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with API keys

# Run local development server
uvicorn main:app --reload --port 8000

# Run tests
pytest
pytest -v  # Verbose output
pytest tests/test_search_handler.py  # Specific test file
pytest -k "test_search"  # Run tests matching pattern

# Run with coverage
pytest --cov=handlers --cov=clients

# Build Lambda package (Docker-based)
./build_lambda.sh

# Deploy Lambda functions
./deploy.sh
```

### Frontend Development

```bash
# Setup
cd frontend
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with API_URL

# Run development server
npm run dev
# Opens at http://localhost:3000

# Build for production
npm run build
# Generates static files in out/ directory

# Run production build locally
npm run start

# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

### Infrastructure Management

```bash
# Setup
cd infrastructure
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply
terraform apply -auto-approve  # Skip confirmation

# Target specific resources
terraform apply -target=aws_lambda_function.search_handler

# Destroy resources
terraform destroy

# View state
terraform show
terraform state list

# Quick deploy script
./quick_deploy.sh
```

### Deployment Commands

```bash
# Frontend deployment (FULL REBUILD)
cd frontend
rm -rf .next out  # Clean cache
npm run build
aws s3 sync out/ s3://seodaily-eng-frontend-dev-us-east-1/ --delete
aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"

# Backend deployment
cd backend
./build_lambda.sh  # Builds and uploads to S3, updates Lambda

# Infrastructure deployment
cd infrastructure
terraform apply -auto-approve
```

### Monitoring Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1
aws logs tail /aws/lambda/seodaily-eng-search-dev --follow --region us-east-1
aws logs tail /aws/lambda/seodaily-eng-article-dev --follow --region us-east-1

# Check EventBridge rule
aws events describe-rule --name seodaily-eng-article-collection-dev --region us-east-1

# Manual Lambda trigger
aws lambda invoke \
  --function-name seodaily-eng-article-collector-dev \
  --payload '{"hours": 1}' \
  --region us-east-1 \
  response.json

# Check DynamoDB item count
aws dynamodb scan --table-name seodaily-eng-articles-dev --select COUNT --region us-east-1

# Query recent articles
aws dynamodb query \
  --table-name seodaily-eng-articles-dev \
  --index-name category-published_at-index \
  --key-condition-expression "category = :cat" \
  --expression-attribute-values '{":cat":{"S":"경제"}}' \
  --scan-index-forward false \
  --limit 10 \
  --region us-east-1
```

## Build Systems

### Backend Build
- **Docker**: Linux-compatible Lambda package building
- **build_lambda.sh**: Automated build script
  - Creates Docker container with Python 3.11
  - Installs dependencies in Linux environment
  - Packages handlers, clients, config, TRANSLATION_PROMPT.md
  - Uploads to S3
  - Updates Lambda function code

### Frontend Build
- **Next.js Static Export**: Generates static HTML/CSS/JS
- **SWC**: Fast TypeScript/JavaScript compilation
- **Webpack**: Module bundling (via Next.js)
- **Output**: Static files in out/ directory
  - 15 static pages
  - 97.1kB First Load JS
  - ~15 second build time

### Infrastructure Build
- **Terraform**: Declarative infrastructure provisioning
- **State Management**: terraform.tfstate tracks resources
- **Provider Plugins**: AWS provider auto-downloaded

## Configuration Management

### Backend Configuration
```python
# config.py - Pydantic Settings
class Settings(BaseSettings):
    bigkinds_api_key: str
    anthropic_api_key: str
    anthropic_model_id: str = "claude-opus-4-5-20251101"
    region: str = "us-east-1"
    articles_table: str = "seodaily-eng-articles-dev"
    metadata_table: str = "seodaily-eng-metadata-dev"
    
    class Config:
        env_file = ".env"
```

### Frontend Configuration
```javascript
// next.config.js
module.exports = {
  output: 'export',
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    optimizePackageImports: ['lucide-react']
  }
}
```

### Infrastructure Configuration
```hcl
# terraform.tfvars
region = "us-east-1"
environment = "dev"
project_name = "seodaily-eng"
lambda_memory = 1024
lambda_timeout = 60
```

## Environment Variables

### Backend (.env)
```bash
BIGKINDS_API_KEY=254bec69-1c13-470f-904a-c4bc9e46cc80
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
AWS_REGION=us-east-1
ARTICLES_TABLE=seodaily-eng-articles-dev
METADATA_TABLE=seodaily-eng-metadata-dev
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
```

### Lambda Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL_ID=claude-opus-4-5-20251101
```

## Version Control

### Git Configuration
- **Repository**: Local Git repository
- **.gitignore**: Excludes build artifacts, dependencies, secrets
  - `node_modules/`, `.next/`, `out/`
  - `venv/`, `__pycache__/`, `*.pyc`
  - `.env`, `.env.local`
  - `terraform.tfstate`, `.terraform/`
  - `lambda_package.zip`

## Performance Optimizations

### Backend
- **Async Operations**: All I/O operations use async/await
- **Batch Processing**: DynamoDB batch_get_item (100 items)
- **Chunked Translation**: 4,000 character chunks for large articles
- **Lambda Memory**: 1024MB for 2x CPU performance
- **Connection Pooling**: httpx client reuse

### Frontend
- **Static Generation**: Pre-rendered HTML at build time
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Unused code elimination
- **Minification**: JavaScript and CSS minification
- **Compression**: Gzip compression enabled
- **Image Optimization**: Next.js Image component (not used - text-only)
- **Font Optimization**: Google Fonts with preconnect

### Infrastructure
- **CloudFront CDN**: Global edge caching
- **DynamoDB GSI**: Optimized category queries
- **Lambda Warm Start**: 1024MB reduces cold start time
- **API Gateway Caching**: Available but not enabled (cost consideration)

## Development Tools

### Code Quality
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting (via ESLint)
- **TypeScript**: Static type checking
- **Pytest**: Python testing framework

### Debugging
- **Chrome DevTools**: Frontend debugging
- **React DevTools**: Component inspection
- **CloudWatch Logs**: Lambda debugging
- **FastAPI Docs**: Auto-generated API documentation at /docs

### Monitoring
- **CloudWatch**: AWS service monitoring
- **Lambda Insights**: Performance metrics
- **Google Search Console**: SEO monitoring
- **Lighthouse**: Performance auditing
