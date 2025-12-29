# Project Structure

## Directory Organization

```
SEOdaily-ENG/
├── backend/              # Python FastAPI backend + Lambda handlers
├── frontend/             # Next.js 14 TypeScript frontend
├── infrastructure/       # Terraform IaC for AWS resources
├── cms/                  # Content Management System (future)
├── archive/              # Historical scripts and documentation
└── docs/                 # Project documentation
```

## Backend Structure

```
backend/
├── clients/              # External service integrations
│   ├── bigkinds_client.py       # BigKinds API wrapper
│   ├── dynamodb_client.py       # DynamoDB operations
│   ├── translation_service.py   # Anthropic Claude integration
│   ├── response_validator.py    # API response validation
│   ├── cache_manager.py         # Redis caching layer
│   └── validation.py            # Input validation utilities
├── handlers/             # Lambda function handlers
│   ├── article_collector.py     # Hourly article collection
│   ├── article_handler.py       # Article detail API
│   ├── search_handler.py        # Search API with filtering
│   ├── admin_handler.py         # Admin operations
│   └── error_handler.py         # Centralized error handling
├── tests/                # Comprehensive test suite
│   ├── test_bigkinds_client.py
│   ├── test_search_handler.py
│   ├── test_article_handler.py
│   └── conftest.py              # Pytest configuration
├── config.py             # Configuration management
├── main.py               # FastAPI application entry
├── requirements.txt      # Python dependencies
├── build_lambda.sh       # Docker-based Lambda packaging
└── TRANSLATION_PROMPT.md # Claude translation instructions
```

### Backend Components

**BigKinds Client**
- Interfaces with BigKinds API for Seoul Economic articles
- Handles search queries with field selection
- Fetches article details with full content
- Automatic HTTPS conversion for links
- Rate limiting and error handling

**DynamoDB Client**
- Article storage and retrieval operations
- Batch duplicate checking (91% call reduction)
- Category-based queries with GSI
- Save verification with read-after-write
- Proper type handling (List → String conversion)

**Translation Service**
- Anthropic Claude Opus 4.5 integration
- Chunked translation for large articles (4,000 char limit)
- Structured output parsing (HEADLINE, BYLINE, ARTICLE, SEO/AEO)
- Professional journalism quality translation
- Comprehensive error handling and retries

**Article Collector**
- EventBridge-triggered hourly execution
- Today's articles collection (00:00-23:59 KST)
- Smart deduplication before translation
- Content filtering (skip empty articles)
- Batch processing (100 articles per API call)

**Search Handler**
- Title + content search with case-insensitive matching
- Date range filtering (30 days default)
- Content validation (exclude empty articles)
- Pagination support
- DynamoDB scan with filtering

**Article Handler**
- Article detail retrieval by news_id
- Related articles recommendation (same category)
- SEO metadata inclusion (meta_description, keywords, hashtags)
- DynamoDB caching (0.5s cached, 2.5s uncached)
- Comprehensive error responses

## Frontend Structure

```
frontend/
├── src/
│   ├── app/              # Next.js 14 App Router
│   │   ├── layout.tsx           # Root layout with metadata
│   │   ├── page.tsx             # Homepage (client-side loading)
│   │   ├── [category]/          # Dynamic category pages
│   │   │   ├── page.tsx         # Server wrapper
│   │   │   └── CategoryClient.tsx # Client component
│   │   ├── article/             # Article detail page
│   │   │   └── page.tsx         # Universal article template
│   │   ├── search/              # Search page
│   │   │   └── page.tsx         # Search with pagination
│   │   ├── robots.ts            # SEO robots configuration
│   │   ├── sitemap.ts           # Static sitemap generation
│   │   └── opengraph-image.tsx  # OG image generation
│   ├── components/       # React components
│   │   ├── common/              # Shared components
│   │   │   ├── Header/          # Navigation header
│   │   │   ├── Footer/          # Site footer
│   │   │   └── Breadcrumb/      # Navigation breadcrumbs
│   │   └── home/                # Homepage components
│   │       ├── HeroSection/     # Featured articles
│   │       ├── SectionGrid/     # Category sections
│   │       └── Newsletter/      # Email subscription
│   ├── types/            # TypeScript type definitions
│   │   └── article.ts           # Article interfaces
│   ├── utils/            # Utility functions
│   │   ├── api.ts               # Centralized API calls
│   │   └── formatDate.ts        # Date formatting
│   └── constants/        # Application constants
├── public/               # Static assets
│   ├── sedaily-logo.jpg         # Seoul Economic logo
│   └── sedaily-logo.svg         # Logo SVG version
├── next.config.js        # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── tsconfig.json         # TypeScript configuration
```

### Frontend Components

**Layout System**
- Root layout with SEO metadata and Google verification
- Header with smart scroll behavior (hides on scroll >100px)
- Seoul Economic logo linking to main site
- Footer with links and copyright
- Responsive design for all screen sizes

**Homepage**
- Client-side data loading with useEffect
- Featured article (50%) + Most Popular (50%) layout
- Top Stories horizontal grid (5 columns)
- Section grids for Finance, Technology, Society
- JSON-LD structured data for SEO

**Category Pages**
- Server/client component separation
- Chosun Daily style layout (67% main + 33% sidebar)
- 15 articles per category
- Most Read sidebar (5 articles)
- Category-specific filtering

**Article Detail**
- Universal template for all articles
- Query parameter routing (?id=xxx)
- Related articles (3 from same category)
- SEO metadata display (hashtags, keywords)
- JSON-LD NewsArticle schema
- Breadcrumb navigation

**Search Page**
- Real-time search with API integration
- Title + content matching
- Keyword highlighting
- Client-side pagination
- Loading and error states

## Infrastructure Structure

```
infrastructure/
├── main.tf               # Core AWS resources
│   ├── Lambda functions (search, article, collector)
│   ├── API Gateway REST API
│   ├── IAM roles and policies
│   └── CloudWatch log groups
├── dynamodb_articles.tf  # DynamoDB tables
│   ├── Articles table with GSI
│   └── Metadata table
├── eventbridge.tf        # Scheduled events
│   └── Hourly article collection
├── terraform.tfvars      # Environment variables
└── .terraform/           # Terraform state
```

### Infrastructure Components

**Lambda Functions**
- `seodaily-eng-search-dev`: Search API (1024MB)
- `seodaily-eng-article-dev`: Article detail API (1024MB)
- `seodaily-eng-article-collector-dev`: Hourly collector (1024MB)
- All functions use Python 3.11 runtime
- Environment variables for API keys
- CloudWatch logging enabled

**DynamoDB Tables**
- `seodaily-eng-articles-dev`: Main article storage
  - Primary key: news_id (String)
  - GSI: category-published_at-index
  - 1,475+ articles stored
- `seodaily-eng-metadata-dev`: System metadata

**EventBridge**
- Schedule: rate(1 hour)
- Execution: Every hour at :48 (KST)
- Target: article_collector Lambda
- Payload: {"hours": 1}

**S3 Buckets**
- `seodaily-eng-frontend-dev-us-east-1`: Static frontend files
- `seodaily-eng-lambda-packages-dev`: Lambda deployment packages

**CloudFront**
- Distribution ID: EUWQ1K71CXJUH
- Custom domains: en.sedaily.ai (primary), eng.sedaily.ai (alias)
- SSL certificate from ACM
- Cache invalidation on deployment

## Architectural Patterns

### Event-Driven Architecture
- EventBridge triggers Lambda on schedule
- Asynchronous article collection and translation
- Decoupled components for scalability
- CloudWatch for monitoring and logging

### Serverless Architecture
- No server management required
- Auto-scaling based on demand
- Pay-per-use pricing model
- High availability by default

### Static Site Generation
- Next.js static export to S3
- CloudFront CDN distribution
- Client-side data loading for dynamic content
- No server-side rendering overhead

### API Gateway Pattern
- RESTful API endpoints
- Lambda proxy integration
- CORS enabled for frontend
- Request/response transformation

### Caching Strategy
- DynamoDB as primary cache
- Article deduplication before translation
- Batch checking for efficiency
- Read-after-write verification

## Data Flow

### Article Collection Flow
```
EventBridge (hourly trigger)
  ↓
Lambda Collector
  ↓
BigKinds API (search today's articles)
  ↓
DynamoDB (batch duplicate check)
  ↓
Anthropic Claude (translate new articles)
  ↓
DynamoDB (save with SEO metadata)
  ↓
CloudWatch (logging)
```

### Frontend Display Flow
```
User visits page
  ↓
Client-side useEffect
  ↓
API Gateway
  ↓
Lambda Handler
  ↓
DynamoDB Query
  ↓
JSON Response
  ↓
React State Update
  ↓
UI Render
```

### Search Flow
```
User enters query
  ↓
Search API call
  ↓
Lambda Search Handler
  ↓
DynamoDB Scan with filter
  ↓
Title + Content matching
  ↓
Filtered results
  ↓
Paginated response
```

## Component Relationships

### Backend Dependencies
- `bigkinds_client` → `response_validator` → `validation`
- `article_collector` → `bigkinds_client` + `translation_service` + `dynamodb_client`
- `search_handler` → `dynamodb_client` + `error_handler`
- `article_handler` → `dynamodb_client` + `error_handler`

### Frontend Dependencies
- `page.tsx` → `utils/api.ts` → API Gateway
- `CategoryClient` → `utils/api.ts` → `types/article.ts`
- `Header` → `Search` → `search/page.tsx`
- `article/page.tsx` → Related Articles → `utils/api.ts`

### Infrastructure Dependencies
- Lambda → DynamoDB (read/write)
- Lambda → Anthropic API (translation)
- Lambda → BigKinds API (article source)
- EventBridge → Lambda (scheduled trigger)
- CloudFront → S3 (static files)
- API Gateway → Lambda (proxy integration)
