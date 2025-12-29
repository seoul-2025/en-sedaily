# Product Overview

## Project Purpose

SEOdaily-ENG is an automated English news portal that translates Korean business and financial news from Seoul Economic Daily into professional English content. The platform provides real-time access to Korean business news for international audiences through AI-powered translation and automated content delivery.

## Value Proposition

- **Real-time Translation**: Automatically translates Korean business news to English every hour using Anthropic Claude Opus 4.5
- **Professional Quality**: WSJ/FT/Reuters/Bloomberg-level journalism quality through advanced AI translation
- **Zero Manual Intervention**: Fully automated collection, translation, and publishing pipeline
- **Cost Efficient**: 83% cost reduction vs AWS Translate while delivering 10x better quality
- **SEO Optimized**: Complete SEO/AEO optimization for Google Search, Perplexity, ChatGPT discovery

## Key Features

### Automated Content Pipeline
- **Hourly Collection**: EventBridge triggers article collection every hour at :48 (KST)
- **Smart Deduplication**: 91% reduction in DynamoDB calls through batch checking
- **Content Filtering**: Only articles with substantive content are processed
- **Chunked Translation**: Handles large articles by splitting into 4,000 character chunks
- **Original Links**: Preserves direct links to Seoul Economic source articles

### Translation Excellence
- **Anthropic Claude Opus 4.5**: Professional-grade economic journalism translation
- **Structured Output**: HEADLINE, BYLINE, ARTICLE, DISCLAIMER, SEO/AEO sections
- **Context Preservation**: Maintains facts, nuance, and tone from original Korean
- **SEO Metadata**: Automatic generation of meta descriptions, keywords, hashtags, Q&A

### User Experience
- **Client-Side Loading**: Latest articles appear on page refresh without frontend rebuild
- **7 Categories**: Finance, Technology, Politics, Society, Culture, Sports, International
- **Search Functionality**: Title + content search with case-insensitive matching
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Premium Theme**: Seoul Economic white theme with Noto Sans typography

### Performance
- **Fast Loading**: 97.1kB First Load JS, 40% faster initial load (15 articles)
- **Quick API**: 2.5s response time (50% improvement with 1024MB Lambda)
- **Static Export**: Next.js static generation for optimal CDN delivery
- **Core Web Vitals**: Optimized compression, minification, resource hints

### SEO/AEO Optimization
- **Google Search Console**: Verified and configured
- **Structured Data**: JSON-LD schemas for WebSite and NewsArticle
- **Open Graph**: Custom brand images (1200x630px)
- **Sitemap**: Static sitemap with 9 main pages
- **Answer Engine Ready**: Optimized for Perplexity, ChatGPT, Claude

## Target Users

### Primary Audience
- **International Investors**: Seeking Korean business news in English
- **Financial Analysts**: Monitoring Korean market developments
- **Business Professionals**: Following Korean economic trends
- **Journalists**: Researching Korean business stories
- **Researchers**: Studying Korean economy and markets

### Secondary Audience
- **Korean Diaspora**: English-speaking Koreans abroad
- **Students**: Learning about Korean business environment
- **Policy Makers**: Tracking Korean economic policy
- **Tech Industry**: Following Korean tech sector news

## Use Cases

### Investment Research
- Monitor Korean stock market developments in real-time
- Track major corporate announcements and earnings
- Follow regulatory changes affecting Korean markets
- Research Korean companies for investment decisions

### Business Intelligence
- Stay updated on Korean business trends
- Monitor competitor activities in Korean market
- Track industry developments and innovations
- Understand Korean economic policy impacts

### News Aggregation
- Integrate Korean business news into global news feeds
- Provide Korean perspective in international coverage
- Cross-reference Korean sources with global reporting
- Discover stories before they reach international media

### Academic Research
- Access Korean business news for research papers
- Study Korean economic developments over time
- Analyze Korean media coverage of business events
- Compare Korean and international business reporting

## Competitive Advantages

1. **Automation**: Zero manual translation effort required
2. **Quality**: Professional journalism quality through Claude Opus 4.5
3. **Speed**: Hourly updates ensure timely content delivery
4. **Cost**: $71/month total operational cost
5. **Scalability**: Serverless architecture handles unlimited traffic
6. **SEO**: Complete optimization for search and answer engines
7. **Reliability**: 100% save success rate, comprehensive error handling
8. **Integration**: Direct links to original Seoul Economic articles

## Success Metrics

- **Total Articles**: 1,475+ and continuously growing
- **Collection Success**: 100% save rate after Phase 11 fixes
- **Translation Quality**: WSJ/FT/Reuters/Bloomberg professional level
- **Performance**: 40% faster homepage, 50% faster API responses
- **Cost Efficiency**: 83% savings vs AWS Translate
- **Deduplication**: 96% translation cost reduction through smart caching
- **SEO Status**: Google Search Console verified, sitemap submitted
