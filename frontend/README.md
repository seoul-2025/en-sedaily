# Seoul Economic Daily - English Frontend

English version of Seoul Economic Daily news portal with Server-Side Rendering (SSR).

## Tech Stack

- **Framework**: Next.js 14.2.0 (App Router, SSR)
- **Language**: TypeScript 5.3.0
- **Styling**: Tailwind CSS 3.4.0
- **Icons**: Lucide React 0.344.0
- **Build**: Standalone (SSR with PM2)
- **Deployment**: EC2 + CloudFront + PM2

## Project Structure

```
src/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage
│   ├── [category]/         # Category pages
│   ├── article/            # Article detail pages
│   ├── search/             # Search page
│   └── globals.css         # Global styles
├── components/
│   ├── common/
│   │   ├── Header/         # Header component
│   │   ├── Footer/         # Footer component
│   │   ├── Breadcrumb/     # Breadcrumb navigation
│   │   └── LoadingSpinner/ # Loading spinner
│   ├── home/
│   │   ├── HeroSection/    # Hero section
│   │   ├── SectionGrid/    # Section grid
│   │   └── Newsletter/     # Newsletter
│   └── article/
│       ├── ArticleImage/   # Article image component
│       └── ShareButtons/   # Social sharing buttons
├── constants/
│   └── categories.ts       # Category definitions
├── types/
│   └── article.ts          # TypeScript types
├── hooks/
│   └── useTheme.ts         # Theme hook
├── lib/
│   └── api-config.ts       # API configuration
└── utils/
    ├── api.ts              # API functions
    ├── formatDate.ts       # Date utilities
    └── imageUrl.ts         # Image URL utilities
```

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

Open http://localhost:3000

### Build for Production
```bash
npm run build
```

Output: `.next/standalone/` directory (SSR build)

## Environment Variables

Create `.env.local`:
```
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_API_URL=https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
```

## Deployment Architecture

```
Internet → CloudFront (EUWQ1K71CXJUH) → EC2 (52.21.195.0) → PM2 → Next.js SSR
           SSL/CDN                        Nginx Proxy        Process Manager
```

### Current Deployment Process

**Automated via `deploy.sh`:**
1. Build Next.js standalone application
2. Package with dependencies and static files
3. Upload to EC2 via SCP
4. Deploy with PM2 process manager
5. Verify deployment health

```bash
# Deploy to production
./deploy.sh
```

### Manual Deployment Steps

If needed, individual steps:
```bash
# 1. Build
npm run build

# 2. Package
cp -r .next/standalone/* deploy-package/
cp -r .next/static deploy-package/.next/
cp -r public deploy-package/

# 3. Upload and deploy
# (See deploy.sh for full process)
```

### Infrastructure Details

- **EC2 Instance**: i-05298ffc0455ee5ce (t3.small)
- **CloudFront**: EUWQ1K71CXJUH (en.sedaily.ai, en.sedaily.com)
- **PM2 App**: sedaily-eng
- **Nginx**: Reverse proxy with SSL termination
- **API Gateway**: 7w5nco7xn4 (backend API)

## Components

### Header
- Logo (Georgia font)
- Category navigation
- Search functionality
- Sticky header with scroll behavior

### Hero Section
- Featured article (50% width)
- Top stories (25% width)
- Most popular (25% width)
- Responsive grid layout

### Section Grid
- Latest Business
- Market Watch
- Tech Trends
- Dynamic content loading

### Article Pages
- Full article content
- Related articles
- Social sharing
- Breadcrumb navigation

### Newsletter
- Email subscription form
- API integration for subscriptions

### Footer
- Navigation links
- Social media icons
- Copyright and legal information

## Design System

### Colors
- Primary: #2c3e50 (Navy)
- Featured: #e74c3c (Red)
- Accent: #0066cc (Blue)
- Text: #333333 (Dark Gray)

### Typography
- Logo: Georgia, serif
- Headlines: Inter, sans-serif (600/700 weight)
- Body: Inter, sans-serif (400/500 weight)

### Breakpoints
- Desktop: 1200px+
- Tablet: 768-1199px
- Mobile: < 768px

## API Integration

### Backend Integration
All API calls go through AWS API Gateway:
```typescript
// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
```

### Fetch Latest Articles
```typescript
import { fetchLatestArticles } from '@/utils/api';

const data = await fetchLatestArticles(category, limit);
```

### Fetch Article Detail
```typescript
import { fetchArticleDetail } from '@/utils/api';

const article = await fetchArticleDetail(articleId);
```

### Search Articles
```typescript
import { searchArticles } from '@/utils/api';

const results = await searchArticles(query);
```

## SEO Optimization

- **Meta Tags**: Dynamic meta tags per page
- **Open Graph**: Social media sharing optimization
- **Twitter Cards**: Twitter-specific meta tags
- **Structured Data**: JSON-LD for articles
- **Sitemap**: Automated sitemap.xml generation
- **Robots.txt**: Search engine crawling rules

## Performance

### Metrics
- **First Load JS**: ~87 kB
- **SSR**: Server-side rendering for SEO
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Inter font with display swap

### Optimizations
- Static asset caching (1 year)
- Dynamic content caching (CloudFront)
- Gzip compression (Nginx)
- Code splitting (Next.js)

### Monitoring
- PM2 process monitoring
- CloudWatch logs integration
- Nginx access/error logs
- Application performance metrics

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Tools

### Available Scripts
```bash
npm run dev          # Development server
npm run build        # Production build
npm run start        # Start production server
npm run lint         # ESLint checking
npm run type-check   # TypeScript checking
```

### Utility Scripts
```bash
scripts/
├── deploy-ec2.sh    # Alternative deployment script
└── setup-ec2.sh     # EC2 initial setup script
```

## Production Deployment

### Health Checks
- Application startup verification
- API connectivity checks
- Static asset availability
- PM2 process status monitoring

### Backup & Recovery
- Automated backups before deployment
- Rollback capability in case of failures
- Configuration backup and restore

### SSL & Security
- CloudFront SSL termination
- Nginx security headers
- Rate limiting configuration
- CORS policy implementation

## Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Clear Next.js cache
   rm -rf .next
   npm run build
   ```

2. **PM2 Process Issues**
   ```bash
   # Check PM2 status
   ssh -i sedaily-eng-key.pem ubuntu@52.21.195.0 'pm2 status'
   
   # View logs
   ssh -i sedaily-eng-key.pem ubuntu@52.21.195.0 'pm2 logs'
   ```

3. **CloudFront Cache Issues**
   ```bash
   # Create invalidation
   aws cloudfront create-invalidation --distribution-id EUWQ1K71CXJUH --paths "/*"
   ```

### Monitoring Commands
```bash
# Check deployment status
./deploy.sh

# Monitor application logs
pm2 logs sedaily-eng --lines 50

# Check system resources
pm2 monit
```

## License

Proprietary - Seoul Economic Daily