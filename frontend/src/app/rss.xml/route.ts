import { NextResponse } from 'next/server';

const baseUrl = 'https://en.sedaily.com';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

async function getLatestArticles(limit: number = 50) {
    try {
        const response = await fetch(`${API_URL}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: '*',
                filters: {
                    published_from: '2020-01-01',
                    published_until: '2030-12-31',
                },
                page: 1,
                page_size: limit,
                sort_by: 'published_at',
                sort_order: 'desc',
            }),
            cache: 'no-store',
        });

        if (!response.ok) return [];
        const data = await response.json();
        return data.articles || [];
    } catch (error) {
        console.error('Failed to fetch articles for RSS:', error);
        return [];
    }
}

function escapeXml(unsafe: string): string {
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

function getCategoryInEnglish(category: string): string {
    const categoryMap: { [key: string]: string } = {
        '경제': 'Finance',
        'IT_과학': 'Technology',
        '정치': 'Politics',
        '사회': 'Society',
        '문화': 'Culture',
        '스포츠': 'Sports',
        '국제': 'International',
    };
    return categoryMap[category] || category;
}

function buildArticleUrl(article: any): string {
    if (!article.slug) {
        return `${baseUrl}/article?id=${article.news_id}`;
    }

    const date = new Date(article.published_at);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    const categoryMap: { [key: string]: string } = {
        '경제': 'finance',
        'IT_과학': 'technology',
        '정치': 'politics',
        '사회': 'society',
        '문화': 'culture',
        '스포츠': 'sports',
        '국제': 'international',
    };

    const categorySlug = categoryMap[article.category] || 'news';

    return `${baseUrl}/${categorySlug}/${year}/${month}/${day}/${article.slug}`;
}

export async function GET() {
    const articles = await getLatestArticles(50);
    const now = new Date();

    const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Seoul Economic Daily - English Edition</title>
    <link>${baseUrl}</link>
    <description>Korea's leading economic newspaper. Latest business news, stock market, economy, finance, and technology updates in English.</description>
    <language>en-us</language>
    <lastBuildDate>${now.toUTCString()}</lastBuildDate>
    <atom:link href="${baseUrl}/rss.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>${baseUrl}/sedaily-logo.png</url>
      <title>Seoul Economic Daily</title>
      <link>${baseUrl}</link>
    </image>
${articles.map((article: any) => {
    const articleUrl = buildArticleUrl(article);
    const pubDate = new Date(article.published_at).toUTCString();
    const category = getCategoryInEnglish(article.category);
    const description = article.meta_description || article.content?.substring(0, 300) || article.title;

    return `    <item>
      <title>${escapeXml(article.title)}</title>
      <link>${articleUrl}</link>
      <guid isPermaLink="true">${articleUrl}</guid>
      <pubDate>${pubDate}</pubDate>
      <category>${category}</category>
      <description>${escapeXml(description)}</description>
      ${article.byline ? `<dc:creator>${escapeXml(article.byline)}</dc:creator>` : ''}
    </item>`;
}).join('\n')}
  </channel>
</rss>`;

    return new NextResponse(rss, {
        status: 200,
        headers: {
            'Content-Type': 'application/rss+xml; charset=utf-8',
            'Cache-Control': 'public, max-age=1800, s-maxage=1800', // 30 minutes cache
        },
    });
}
