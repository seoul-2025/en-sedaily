import { MetadataRoute } from 'next';
import { buildArticleUrl } from '@/utils/articleUrl';
import { englishToKorean, getCategorySlug } from '@/constants/categoryMapping';

const baseUrl = 'https://en.sedaily.com';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

// Define all categories for sitemap generation
const CATEGORIES = [
    'static',       // Homepage and category pages
    'finance',
    'technology',
    'politics',
    'society',
    'culture',
    'sports',
    'international',
];

// Generate sitemap IDs for each category
export async function generateSitemaps() {
    return CATEGORIES.map(category => ({ id: category }));
}

// Fetch articles for a specific category
async function getArticlesByCategory(category: string) {
    if (category === 'static') return []; // No articles for static pages

    // Convert English category to Korean for API filtering
    const koreanCategories = englishToKorean(category);

    try {
        const allArticles: any[] = [];
        let currentPage = 1;
        const pageSize = 1000;

        // First request to get total pages
        const firstResponse = await fetch(`${API_URL}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: '*',
                filters: {
                    category: koreanCategories,
                    published_from: '2020-01-01',
                    published_until: '2030-12-31',
                },
                page: currentPage,
                page_size: pageSize,
            }),
        });

        if (!firstResponse.ok) return [];
        const firstData = await firstResponse.json();
        allArticles.push(...(firstData.articles || []));

        const totalPages = firstData.total_pages || 1;
        console.log(`Sitemap [${category}]: Fetching ${firstData.total_hits || 0} articles across ${totalPages} pages...`);

        // Fetch remaining pages
        const requests = [];
        for (let page = 2; page <= totalPages; page++) {
            requests.push(
                fetch(`${API_URL}/api/search`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: '*',
                        filters: {
                            category: koreanCategories,
                            published_from: '2020-01-01',
                            published_until: '2030-12-31',
                        },
                        page,
                        page_size: pageSize,
                    }),
                })
            );
        }

        // Fetch all pages in parallel (max 10 concurrent requests)
        const batchSize = 10;
        for (let i = 0; i < requests.length; i += batchSize) {
            const batch = requests.slice(i, i + batchSize);
            const responses = await Promise.all(batch);

            for (const response of responses) {
                if (response.ok) {
                    const data = await response.json();
                    allArticles.push(...(data.articles || []));
                }
            }
        }

        console.log(`Sitemap [${category}]: Successfully fetched ${allArticles.length} articles`);
        return allArticles;
    } catch (error) {
        console.error(`Failed to fetch articles for sitemap [${category}]:`, error);
        return [];
    }
}

// Generate sitemap for a specific category
export default async function sitemap({
    id,
}: {
    id: string;
}): Promise<MetadataRoute.Sitemap> {
    const category = id;

    // Static pages sitemap (homepage, category pages)
    if (category === 'static') {
        return [
            {
                url: baseUrl,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 1.0,
            },
            {
                url: `${baseUrl}/finance`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.9,
            },
            {
                url: `${baseUrl}/technology`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.9,
            },
            {
                url: `${baseUrl}/politics`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.9,
            },
            {
                url: `${baseUrl}/society`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.8,
            },
            {
                url: `${baseUrl}/culture`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.8,
            },
            {
                url: `${baseUrl}/sports`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.8,
            },
            {
                url: `${baseUrl}/international`,
                lastModified: new Date(),
                changeFrequency: 'hourly',
                priority: 0.8,
            },
        ];
    }

    // Category-specific articles
    const articles = await getArticlesByCategory(category);
    const now = new Date();

    return articles
        .filter((article: any) => {
            // Client-side filtering for extra safety
            if (!article.slug) return false; // Only SEO-friendly URLs

            // Ensure article matches the current category
            const articleCategory = Array.isArray(article.category)
                ? article.category[0]
                : article.category;
            const articleCategorySlug = getCategorySlug(articleCategory || 'news');

            return articleCategorySlug === category;
        })
        .map((article: any) => {
            const articlePath = buildArticleUrl({
                news_id: article.news_id,
                slug: article.slug,
                published_at: article.published_at,
                category: article.category
            });

            // Calculate article age for priority (GEO/AEO optimization)
            const publishedDate = new Date(article.published_at);
            const daysOld = Math.floor((now.getTime() - publishedDate.getTime()) / (1000 * 60 * 60 * 24));

            // Priority based on freshness (critical for AI crawlers)
            let priority = 0.5; // Default for old articles (6+ months)
            if (daysOld < 1) {
                priority = 1.0; // Today's breaking news
            } else if (daysOld < 7) {
                priority = 0.9; // This week
            } else if (daysOld < 30) {
                priority = 0.8; // This month
            } else if (daysOld < 90) {
                priority = 0.7; // Last 3 months
            } else if (daysOld < 180) {
                priority = 0.6; // Last 6 months
            }

            return {
                url: `${baseUrl}${articlePath}`,
                lastModified: publishedDate,
                changeFrequency: 'never' as const, // Articles don't change
                priority,
            };
        });
}
