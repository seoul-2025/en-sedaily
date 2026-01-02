# SEOdaily-ENG

English version of Seoul Economic Daily - Korean business news translated to English.

**Last Updated**: 2025-12-31
**Development Method**: AI-Assisted Development (Claude Code)
**Tech Stack**: Next.js + AWS Lambda + Anthropic Claude

---

## Project Overview

SEOdaily-ENG is the official English version of Seoul Economic Daily's website, providing **real-time translation** of Korean business and financial news. Articles are automatically collected every hour from BigKinds API and translated using Anthropic Claude Opus 4.5.

**Live Production**: https://en.sedaily.com
**Target Audience**: Global readers, international investors, English-speaking professionals
**Primary Language**: English (translated from Korean)
**Content Source**: Seoul Economic Daily via BigKinds API
**Update Frequency**: Every hour at :48 (KST)

---

## Quick Start

### Prerequisites

```bash
# Required versions
Node.js >= 18.0.0
Python >= 3.11
AWS CLI configured
Terraform >= 1.5.0
Docker (for Lambda builds)

# Required AWS credentials
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION=us-east-1
```

### Installation

```bash
# Clone repository
git clone git@github.com:sedaily/seodaily-eng.git
cd seodaily-eng

# Install frontend dependencies
cd frontend && npm install

# Install backend dependencies
cd ../backend && pip install -r requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Edit .env with your API keys

cp frontend/.env.example frontend/.env.local
# Edit .env.local with API Gateway URL
```

### Development

```bash
# Run frontend locally
cd frontend && npm run dev
# Opens http://localhost:3000

# Run backend locally (FastAPI)
cd backend && uvicorn main:app --reload
# Opens http://localhost:8000

# Test Lambda function locally
cd backend
python -c "from handlers.article_collector import lambda_handler; print(lambda_handler({}, {}))"

# Test translation
python -c "from modules.translator import translate_article; print(translate_article('테스트 제목', '테스트 내용'))"
```

### Production Deployment

```bash
# Deploy infrastructure (first time)
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Deploy backend (Lambda functions)
cd ../../backend
./build_lambda.sh
aws lambda update-function-code \
  --function-name seodaily-eng-article-collector-dev \
  --zip-file fileb://lambda_package.zip \
  --region us-east-1

# Deploy frontend (EC2 SSR)
cd ../frontend
npm run build
pm2 restart en-sedaily
```

---

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### 📚 Core Documentation

- **[Development Phases](docs/phases/README.md)** - Complete development history (Phase 1-52)
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design decisions
- **[API Reference](docs/API.md)** - API endpoints and usage
- **[Database Schema](docs/DATABASE.md)** - DynamoDB table structure
- **[How It Works](docs/HOW_IT_WORKS.md)** - System workflow and data flow

### 🛠️ Development Guides

- **[AI Development Guidelines](docs/AI_GUIDELINES.md)** - AI-assisted development practices
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Codebase organization
- **[Environment Variables](docs/ENVIRONMENT.md)** - Configuration guide
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment procedures
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### 📊 Technical Reference

- **[Technical Documentation](docs/TECHNICAL.md)** - Performance, cost, security, monitoring
- **[Work Logs](docs/work-logs/)** - Daily development activity logs
- **[Archive](docs/archive/)** - Historical deployment logs

### 📖 Additional Resources

- **[Frontend README](frontend/README.md)** - Next.js frontend documentation
- **[Backend README](backend/README.md)** - Lambda backend documentation
- **[Infrastructure README](infrastructure/README.md)** - Terraform IaC documentation

---

## Contributing

1. Create feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Follow existing code patterns
   - Lambda handlers in `backend/handlers/`
   - Shared modules in `backend/modules/`
   - Next.js pages in `frontend/src/app/`
   - Utilities in `frontend/src/utils/`

3. Write tests for new features
   ```bash
   cd backend
   python -m pytest tests/
   ```

4. Update documentation
   - Add phase documentation to `docs/phases/PHASE-XX-feature-name.md`
   - Update relevant sections (Architecture, API Endpoints, etc.)
   - Document environment variables in `docs/ENVIRONMENT.md`

5. Create phase documentation for significant features
   ```bash
   # Use the phase template
   cp docs/phases/PHASE-52-connections-game.md docs/phases/PHASE-XX-your-feature.md
   # Update with your feature details
   ```

6. Create pull request with detailed description
   - What was changed and why
   - Testing performed
   - Screenshots (if UI changes)
   - Cost/performance impact

---

## License

Proprietary - Seoul Economic Daily

All content translated from Seoul Economic Daily articles. Original content copyright Seoul Economic Daily. Translation and distribution rights reserved.

---

## Contact

- **Team**: Seoul Economic Digital Development Team
- **Email**: dev@sedaily.com
- **Website**: https://www.sedaily.com
- **English Site**: https://en.sedaily.com
- **CMS**: https://enadmin.sedaily.ai

---

Copyright 2025 Seoul Economic Daily. All rights reserved.
