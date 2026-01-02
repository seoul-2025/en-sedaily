## Architecture

```
EventBridge (Every Hour at :48)
         ↓
Lambda Collector (Today's articles)
         ↓
BigKinds API (Seoul Economic only)
         ↓
Anthropic Claude Opus 4.5
         ↓
DynamoDB (Deduplicated storage)
         ↓
API Gateway (Search + Article APIs)
         ↓
EC2 (Next.js SSR + CSR Hybrid)
         ↓
Users (SEO-optimized, real-time)
```

### SSR Architecture (Phase 27)

```
User Request → Nginx (HTTPS) → PM2 → Next.js SSR
                                         ↓
                                   ISR Cache
                                   (5-60 min)
                                         ↓
                                  API Gateway
                                         ↓
                                    DynamoDB
```

### Tech Stack Details

**Frontend**
- Next.js 14.2.0 (App Router)
- TypeScript 5.3.0
- Tailwind CSS 3.4.0
- Server-Side Rendering (SSR)
- Incremental Static Regeneration (ISR)
- Standalone build for EC2

**Backend**
- Python 3.11 + FastAPI
- AWS Lambda (512MB → 1024MB)
- API Gateway (REST API)
- DynamoDB (On-Demand billing)
- EventBridge (Scheduler)
- CloudWatch (Monitoring)

**Infrastructure**
- EC2 t3.medium (2 vCPU, 4GB RAM)
- Nginx + Let's Encrypt SSL
- PM2 Process Manager
- Terraform (IaC)
- S3 (Lambda packages)
- Route53 (DNS)

**AI Translation**
- Anthropic Claude Opus 4.5
- Model: claude-opus-4-5-20251101
- Input: 3,000 tokens avg
- Output: 1,500 tokens avg
- Cost: $0.019/article

**Analytics & Monetization**
- Google Analytics 4 (GA4)
  - Measurement ID: G-1MCM9W4BVH
  - Automatic event tracking (page views, article views, searches)
  - Custom dimensions and conversions
  - Real-time user behavior analysis
- Google AdSense (Code Prepared)
  - Ad placement: Articles (3), Homepage (2), Categories (2)
  - Ad formats: Leaderboard, In-Article, Sidebar
  - Status: Awaiting account approval

**Deployment**
- Automated deployment script (deploy.sh)
- Standalone Next.js build with .env.local auto-inclusion
- PM2 with dynamic environment variable loading
- CloudFront CDN with cache invalidation
- Zero-downtime deployment with automatic backup

---

