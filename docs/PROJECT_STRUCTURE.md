## Project Structure

```
seodaily-eng/
├── frontend/                       # Next.js SSR application
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   │   ├── page.tsx           # Homepage
│   │   │   ├── [category]/        # Category pages
│   │   │   ├── [category]/[year]/[month]/[day]/[slug]/  # SEO-friendly article URLs
│   │   │   ├── article/[id]/      # Legacy article detail (redirects)
│   │   │   ├── search/            # Search page
│   │   │   ├── about/             # E-E-A-T pages
│   │   │   ├── contact/
│   │   │   ├── terms/
│   │   │   └── privacy/
│   │   ├── components/            # Reusable components
│   │   ├── utils/                 # Utility functions
│   │   │   ├── api.ts             # Centralized API calls
│   │   │   ├── articleUrl.ts      # SEO URL generation
│   │   │   ├── formatDate.ts      # Date formatting & relative time
│   │   │   ├── categoryUtils.ts   # Category translation
│   │   │   └── reporterNames.ts   # Byline romanization
│   │   └── types/                 # TypeScript definitions
│   ├── public/
│   │   ├── llms.txt               # AI crawler navigation
│   │   ├── robots.txt             # SEO directives
│   │   └── sitemap.xml            # Dynamic sitemap
│   ├── next.config.js             # Next.js configuration
│   ├── middleware.ts              # ISR cache headers
│   └── package.json
│
├── backend/                        # Serverless backend
│   ├── handlers/                  # Lambda functions
│   │   ├── article_collector.py   # Auto-collection (hourly)
│   │   ├── search_handler.py      # Search API
│   │   ├── article_handler.py     # Article detail API
│   │   └── cms_update_handler.py  # CMS update API
│   ├── clients/                   # AWS service clients
│   │   ├── dynamodb_client.py     # DynamoDB operations
│   │   └── translation_service.py # Anthropic Claude API
│   ├── utils/                     # Utility functions
│   │   ├── date_utils.py          # Timestamp extraction from news_id
│   │   └── slug_generator.py      # SEO-friendly slug generation
│   ├── scripts/                   # Migration & utility scripts
│   │   ├── migrate_timestamps.py  # Update timestamps from news_id
│   │   ├── migrate_categories_to_korean.py  # Category unification
│   │   └── migrate_slugs.py       # Generate slugs for existing articles
│   ├── prompts/
│   │   └── TRANSLATION_PROMPT.md  # Claude translation prompt
│   ├── tests/                     # Unit tests
│   ├── build_lambda.sh            # Docker-based build
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment template
│
├── infrastructure/                 # Infrastructure as Code
│   ├── terraform/                 # Terraform configurations
│   │   ├── main.tf                # Main resources
│   │   ├── lambda.tf              # Lambda functions
│   │   ├── dynamodb.tf            # Database tables
│   │   ├── api_gateway.tf         # API Gateway
│   │   ├── eventbridge.tf         # Scheduler
│   │   └── variables.tf           # Variables
│   └── scripts/                   # Deployment scripts
│
└── docs/                          # Documentation
    ├── REALTIME_UPDATE_GUIDE.md   # Auto-collection guide
    ├── TRANSLATION_PROMPT.md      # Translation standards
    └── .amazonq/rules/memory-bank/ # Deployment notes
```

---

