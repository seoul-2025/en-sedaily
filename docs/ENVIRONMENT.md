## Environment Variables

### Backend (.env)
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# DynamoDB Tables
DYNAMODB_ARTICLES_TABLE=seodaily-eng-articles-dev
DYNAMODB_METADATA_TABLE=seodaily-eng-metadata-dev

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-xxx
ANTHROPIC_MODEL=claude-opus-4-5-20251101

# BigKinds API
BIGKINDS_API_KEY=254bec69-1c13-470f-904a-c4bc9e46cc80
BIGKINDS_BASE_URL=https://tools.kinds.or.kr

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_DELAY=1.0  # seconds between API calls
```

### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
REVALIDATE_SECRET=d5aed293ec4993ad6b13a4033b3b73986b40206cd6d6f43018b3ec0f01bc2748

# Google Analytics 4 Configuration
# Get your Measurement ID from: https://analytics.google.com > Admin > Data Streams
# Format: G-XXXXXXXXXX
NEXT_PUBLIC_GA4_MEASUREMENT_ID=G-1MCM9W4BVH

# Google AdSense Configuration
# Get your Publisher ID from: https://www.google.com/adsense > Account > Settings
# Format: ca-pub-XXXXXXXXXXXXXXXXX (include the 'ca-' prefix)
# Leave empty until AdSense account is approved
NEXT_PUBLIC_ADSENSE_CLIENT_ID=
```

---

