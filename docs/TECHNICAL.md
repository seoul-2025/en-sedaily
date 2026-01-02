# Technical Documentation

## Performance Metrics

Current production metrics (as of 2025-12-22):

### Frontend Performance
- **TTFB (Time to First Byte)**: < 200ms (SSR cached)
- **FCP (First Contentful Paint)**: < 1.5s
- **LCP (Largest Contentful Paint)**: < 2.5s
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Build Size**: 96.8kB First Load JS
- **ISR Cache Hit Rate**: ~85%

### Backend Performance
- **Lambda Cold Start**: < 500ms (1024MB memory)
- **Lambda Warm Start**: < 100ms
- **API Response Time**: < 1s (cached), < 2.5s (uncached)
- **Translation Time**: 3-5 seconds per article
- **DynamoDB Read Latency**: < 10ms
- **DynamoDB Write Latency**: < 20ms

### Collection Performance
- **Collection Frequency**: Every hour at :48
- **Collection Range**: Today's articles (00:00-23:59 KST)
- **Articles per Collection**: 50-70 articles
- **Daily Articles**: ~2,500-2,700 articles/week
- **Deduplication Rate**: 95%+ (cached articles)
- **Success Rate**: 100% (Phase 11 fixes)

### SEO Performance (Google Search Console)
- **Impressions**: 17,546 (30 days)
- **Clicks**: 66
- **CTR**: 0.38%
- **Average Position**: #8.4 (Korea)
- **Countries**: 130+
- **AI Overview**: Confirmed citation

### Storage
- **Total Articles**: 9,045 (as of 2025-12-23)
- **DynamoDB Size**: ~1.8 GB
- **Average Article Size**: ~200 KB
- **Retention**: Unlimited (no TTL)
- **Migration Status**:
  - 8,670 articles with SEO slugs
  - 8,544 articles with actual timestamps
  - 8,881 articles with Korean categories (164 migrated from English)

---


## Cost Estimation (Monthly)

| Service | Estimated Usage | Estimated Cost |
|---------|----------------|----------------|
| **Anthropic Claude** | 2,500 articles × $0.019 | $47.50 |
| **EC2 (t3.medium)** | 730 hours × $0.042 | $30.66 |
| **Lambda Invocations** | 750 collections × 3 functions | $11.25 |
| **API Gateway** | 1M requests | $3.50 |
| **DynamoDB** | 1.5GB storage, 100K R/W | $3.00 |
| **S3** | 5GB storage, Lambda packages | $2.00 |
| **Route53** | 2 hosted zones | $1.00 |
| **CloudWatch** | Logs and metrics | $2.00 |
| **Data Transfer** | 100GB outbound | $9.00 |
| **Total** | | **~$96/month** |

### Cost Breakdown by Phase

- **Phase 8 Optimization**: Reduced from $86 to $14/month (Lambda only)
- **Phase 14 Claude Migration**: Added $47/month, but 10x better quality
- **Phase 27 SSR Migration**: Added $30/month EC2, removed $8 CloudFront

### Cost Optimization Opportunities

1. **Lambda Memory**: 1024MB → 512MB (save $5/month, slower)
2. **Collection Frequency**: 1 hour → 2 hours (save $23/month, less fresh)
3. **EC2 Reserved Instance**: Save 30% ($10/month) with 1-year commitment
4. **DynamoDB Reserved Capacity**: Save 50% ($1.50/month)

**Recommendation**: Keep current configuration for quality and performance.

---


## Security Considerations

### API Security
- API Gateway with API key authentication
- Rate limiting: 1000 requests/minute per IP
- CORS configured for en.sedaily.com only
- Request validation on all endpoints

### Data Security
- DynamoDB encryption at rest (AWS managed)
- Encryption in transit (HTTPS/TLS 1.3)
- IAM roles with least privilege
- No sensitive data in logs

### Secret Management
- Environment variables via Lambda configuration
- Anthropic API key rotated quarterly
- AWS credentials via IAM roles (no hardcoded keys)
- BigKinds API key monitored for usage

### Frontend Security
- HTTPS only (Let's Encrypt SSL)
- Content Security Policy headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- HSTS header enabled

### Compliance
- No user personal data collected
- No cookies (analytics disabled)
- GDPR compliant (no EU user tracking)
- Copyright: All content from Seoul Economic Daily

---


## Monitoring and Logging

### CloudWatch Logs

**Lambda Functions**
```bash
# Article Collector
/aws/lambda/seodaily-eng-article-collector-dev

# Search Handler
/aws/lambda/seodaily-eng-search-dev

# Article Handler
/aws/lambda/seodaily-eng-article-dev
```

**Log Retention**: 30 days

### CloudWatch Metrics

- Lambda invocations, errors, duration
- API Gateway 4XX/5XX errors, latency
- DynamoDB read/write capacity, throttles
- EC2 CPU, memory, disk usage

### Custom Metrics

```python
# Collection metrics
cloudwatch.put_metric_data(
    Namespace='SEOdaily-ENG',
    MetricData=[
        {
            'MetricName': 'ArticlesCollected',
            'Value': collected_count,
            'Unit': 'Count'
        },
        {
            'MetricName': 'TranslationErrors',
            'Value': error_count,
            'Unit': 'Count'
        }
    ]
)
```

### Alerts

- Lambda errors > 5 in 5 minutes
- API Gateway 5XX > 10 in 5 minutes
- DynamoDB throttles > 0
- EC2 CPU > 80% for 10 minutes
- SSL certificate expiry < 30 days

### Google Search Console

- Impressions, clicks, CTR tracked daily
- Core Web Vitals monitored
- Crawl errors reported weekly
- Sitemap status checked

### Manual Monitoring Commands

```bash
# Check Lambda status
aws lambda get-function --function-name seodaily-eng-article-collector-dev --region us-east-1

# View recent logs
aws logs tail /aws/lambda/seodaily-eng-article-collector-dev --follow --region us-east-1

# Check DynamoDB item count
aws dynamodb describe-table --table-name seodaily-eng-articles-dev --region us-east-1

# Test API endpoints
curl https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/search?limit=1

# Check EC2 status
pm2 status
pm2 logs en-sedaily --lines 50
```

---

