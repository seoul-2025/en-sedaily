#!/usr/bin/env python3
"""
Sitemap Generator for en.sedaily.com (BACKUP SCRIPT - NOT CURRENTLY USED)
Generates XML sitemaps for all articles in DynamoDB
Optimized for AI crawlers (ChatGPT, Claude, Perplexity, etc.)

⚠️  NOTE: This script is NOT currently used in production.
    Next.js generates sitemaps dynamically via /frontend/src/app/sitemap.ts

USE CASES:
  - Emergency backup if Next.js sitemap fails
  - Debugging DynamoDB article inventory
  - Static sitemap generation for CDN caching (if needed in future)
  - Manual sitemap verification

CURRENT PRODUCTION SITEMAP:
  - Generated dynamically by Next.js at build time and on request
  - URL: https://en.sedaily.com/sitemap.xml
  - Source: /frontend/src/app/sitemap.ts
  - Includes all 9,421+ articles with real-time updates
"""

import boto3
from datetime import datetime
from typing import List, Dict
import xml.etree.ElementTree as ET
from collections import defaultdict

# Configuration
DYNAMODB_TABLE = 'seodaily-eng-articles-dev'
S3_BUCKET = 'seodaily-eng-frontend-dev-us-east-1'
BASE_URL = 'https://en.sedaily.com'
MAX_URLS_PER_SITEMAP = 50000

# Category mapping: Korean -> English slug
CATEGORY_MAP = {
    '경제': 'finance',
    'IT_과학': 'technology',
    '정치': 'politics',
    '사회': 'society',
    '문화': 'culture',
    '스포츠': 'sports',
    '국제': 'international',
    '지역': 'society'  # Regional goes under society
}


def fetch_all_articles() -> List[Dict]:
    """Fetch all articles from DynamoDB"""
    print("📊 Fetching articles from DynamoDB...")
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(DYNAMODB_TABLE)

    articles = []
    scan_kwargs = {}

    while True:
        response = table.scan(**scan_kwargs)
        articles.extend(response.get('Items', []))

        # Check for more pages
        if 'LastEvaluatedKey' not in response:
            break
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        print(f"  ... fetched {len(articles)} articles")

    print(f"✅ Total articles fetched: {len(articles):,}")
    return articles


def group_articles_by_category(articles: List[Dict]) -> Dict[str, List[Dict]]:
    """Group articles by category"""
    print("\n📁 Grouping articles by category...")
    grouped = defaultdict(list)

    for article in articles:
        # Skip articles without slug (can't generate SEO-friendly URL)
        if not article.get('slug'):
            continue

        category = article.get('category', '')
        category_slug = CATEGORY_MAP.get(category, 'news')
        grouped[category_slug].append(article)

    # Print statistics
    for category, items in sorted(grouped.items()):
        print(f"  {category}: {len(items):,} articles")

    return dict(grouped)


def build_article_url(article: Dict, category_slug: str) -> str:
    """Build SEO-friendly URL for article"""
    slug = article.get('slug')
    date_str = article.get('published_at', '')[:10]  # YYYY-MM-DD

    if not slug or not date_str:
        return None

    year, month, day = date_str.split('-')
    return f"{BASE_URL}/{category_slug}/{year}/{month}/{day}/{slug}"


def generate_sitemap_xml(category: str, articles: List[Dict]) -> str:
    """Generate sitemap XML for a category"""
    print(f"\n🔨 Generating sitemap for {category}...")

    # Create XML structure
    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    added_count = 0
    for article in articles:
        url = build_article_url(article, category)
        if not url:
            continue

        # Create URL entry
        url_elem = ET.SubElement(urlset, 'url')

        loc = ET.SubElement(url_elem, 'loc')
        loc.text = url

        # Last modified date (critical for AI crawlers)
        lastmod = ET.SubElement(url_elem, 'lastmod')
        published_at = article.get('published_at', '')
        if published_at:
            # Convert to ISO 8601 format
            try:
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                lastmod.text = dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
            except:
                lastmod.text = published_at[:10]  # Fallback to date only

        # Change frequency (news articles don't change after publication)
        changefreq = ET.SubElement(url_elem, 'changefreq')
        changefreq.text = 'never'

        # Priority
        priority = ET.SubElement(url_elem, 'priority')
        # Recent articles get higher priority
        try:
            from datetime import timezone
            dt_published = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            days_old = (datetime.now(timezone.utc) - dt_published).days
        except:
            days_old = 999

        if days_old < 7:
            priority.text = '0.8'
        elif days_old < 30:
            priority.text = '0.7'
        else:
            priority.text = '0.6'

        added_count += 1

    print(f"  ✅ Added {added_count:,} URLs")

    # Convert to string with XML declaration
    xml_str = ET.tostring(urlset, encoding='unicode', method='xml')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def generate_sitemap_index(categories: List[str]) -> str:
    """Generate sitemap index file"""
    print("\n📑 Generating sitemap index...")

    sitemapindex = ET.Element('sitemapindex')
    sitemapindex.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    # Add main pages sitemap
    sitemap_elem = ET.SubElement(sitemapindex, 'sitemap')
    loc = ET.SubElement(sitemap_elem, 'loc')
    loc.text = f'{BASE_URL}/sitemap-pages.xml'
    lastmod = ET.SubElement(sitemap_elem, 'lastmod')
    lastmod.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

    # Add category sitemaps
    for category in sorted(categories):
        sitemap_elem = ET.SubElement(sitemapindex, 'sitemap')
        loc = ET.SubElement(sitemap_elem, 'loc')
        loc.text = f'{BASE_URL}/sitemap-{category}.xml'
        lastmod = ET.SubElement(sitemap_elem, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

    xml_str = ET.tostring(sitemapindex, encoding='unicode', method='xml')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def generate_pages_sitemap() -> str:
    """Generate sitemap for static pages and category pages"""
    print("\n📄 Generating pages sitemap...")

    urlset = ET.Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    pages = [
        {'url': BASE_URL, 'priority': '1.0', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/finance', 'priority': '0.9', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/technology', 'priority': '0.9', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/politics', 'priority': '0.9', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/society', 'priority': '0.8', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/culture', 'priority': '0.8', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/sports', 'priority': '0.8', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/international', 'priority': '0.8', 'changefreq': 'daily'},
        {'url': f'{BASE_URL}/about', 'priority': '0.5', 'changefreq': 'monthly'},
        {'url': f'{BASE_URL}/contact', 'priority': '0.5', 'changefreq': 'monthly'},
        {'url': f'{BASE_URL}/terms', 'priority': '0.3', 'changefreq': 'yearly'},
        {'url': f'{BASE_URL}/privacy', 'priority': '0.3', 'changefreq': 'yearly'},
    ]

    for page in pages:
        url_elem = ET.SubElement(urlset, 'url')

        loc = ET.SubElement(url_elem, 'loc')
        loc.text = page['url']

        lastmod = ET.SubElement(url_elem, 'lastmod')
        lastmod.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')

        changefreq = ET.SubElement(url_elem, 'changefreq')
        changefreq.text = page['changefreq']

        priority = ET.SubElement(url_elem, 'priority')
        priority.text = page['priority']

    xml_str = ET.tostring(urlset, encoding='unicode', method='xml')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str


def upload_to_s3(filename: str, content: str):
    """Upload sitemap to S3"""
    print(f"☁️  Uploading {filename} to S3...")
    s3 = boto3.client('s3', region_name='us-east-1')

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=content.encode('utf-8'),
        ContentType='application/xml',
        CacheControl='public, max-age=3600'
    )

    print(f"  ✅ Uploaded to s3://{S3_BUCKET}/{filename}")


def main():
    """Main execution"""
    print("=" * 60)
    print("🗺️  SITEMAP GENERATOR FOR EN.SEDAILY.COM")
    print("   Optimized for AI Crawlers (GEO/AEO)")
    print("=" * 60)

    # 1. Fetch all articles
    articles = fetch_all_articles()

    # 2. Group by category
    grouped = group_articles_by_category(articles)

    # 3. Generate category sitemaps
    sitemaps = {}
    for category, category_articles in grouped.items():
        xml_content = generate_sitemap_xml(category, category_articles)
        sitemaps[f'sitemap-{category}.xml'] = xml_content

    # 4. Generate pages sitemap
    pages_xml = generate_pages_sitemap()
    sitemaps['sitemap-pages.xml'] = pages_xml

    # 5. Generate sitemap index
    index_xml = generate_sitemap_index(list(grouped.keys()))
    sitemaps['sitemap.xml'] = index_xml

    # 6. Upload to S3
    print("\n" + "=" * 60)
    print("📤 UPLOADING TO S3")
    print("=" * 60)

    for filename, content in sitemaps.items():
        upload_to_s3(filename, content)

    print("\n" + "=" * 60)
    print("✅ SITEMAP GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\n📍 Main sitemap: {BASE_URL}/sitemap.xml")
    print(f"📊 Total sitemaps: {len(sitemaps)}")
    print(f"📰 Total articles: {sum(len(arts) for arts in grouped.values()):,}")
    print("\n💡 Next steps:")
    print("   1. Verify sitemaps at https://en.sedaily.com/sitemap.xml")
    print("   2. Submit to Google Search Console")
    print("   3. Update robots.txt with sitemap location")


if __name__ == '__main__':
    main()
