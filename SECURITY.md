# Security Guidelines

## Environment Variables Setup

**⚠️ NEVER commit API keys or secrets to Git!**

### Backend Setup

1. Copy the example file:
```bash
cp backend/.env.example backend/.env
```

2. Fill in your actual values:
```bash
# backend/.env
BIGKINDS_API_KEY=your_actual_bigkinds_api_key
ANTHROPIC_API_KEY=your_actual_anthropic_api_key
AWS_ACCESS_KEY_ID=your_actual_aws_access_key
AWS_SECRET_ACCESS_KEY=your_actual_aws_secret_key
# ... other values
```

### Frontend Setup

1. Copy the example file:
```bash
cp frontend/.env.example frontend/.env.local
```

2. Fill in your actual values:
```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=https://your-actual-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev
# ... other values
```

## Required API Keys

### BigKinds API
- Get your API key from: https://www.bigkinds.or.kr/
- Used for: Korean news article collection

### Anthropic Claude API
- Get your API key from: https://console.anthropic.com/
- Used for: Korean to English translation
- Model: claude-opus-4-5-20251101

### AWS Credentials
- Create IAM user with appropriate permissions
- Required services: Lambda, DynamoDB, API Gateway, S3, CloudWatch
- Used for: All AWS infrastructure

## Security Checklist

- [ ] All `.env*` files are in `.gitignore`
- [ ] No hardcoded API keys in source code
- [ ] AWS credentials configured via IAM roles (production)
- [ ] API keys rotated regularly
- [ ] Environment variables validated before deployment

## Production Deployment

For production, use AWS Systems Manager Parameter Store or AWS Secrets Manager instead of environment variables:

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

## Reporting Security Issues

If you find a security vulnerability, please email: security@sedaily.com