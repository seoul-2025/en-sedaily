/**
 * API Client for Seoul Economic Daily
 *
 * This module provides functions to interact with the backend API.
 * All functions use Next.js fetch with ISR (Incremental Static Regeneration).
 *
 * API Base URL: AWS API Gateway
 * - Development: https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev
 * - Production: Same (dev environment)
 *
 * Caching Strategy:
 * - Latest articles: 600s (10 minutes)
 * - Article detail: 3600s (1 hour)
 * - Category pages: Dynamic (no cache)
 * - Related articles: 1800s (30 minutes)
 * - Search results: 300s (5 minutes)
 */

import { CategoryArticle, ArticleDetail } from "@/types/article";
import { englishToKorean } from "@/constants/categoryMapping";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

// Re-export for backwards compatibility
export type { CategoryArticle };

/**
 * Search API response structure
 */
export interface SearchResponse {
  articles: CategoryArticle[];
  total_hits: number;
  total_pages: number;
  page: number;
  page_size: number;
}

/**
 * Fetch latest articles from all categories
 *
 * @param days - Number of days to fetch (currently unused, legacy parameter)
 * @param pageSize - Articles per page (default: 15)
 * @param page - Page number for pagination (default: 1)
 * @returns Promise<SearchResponse> - Paginated article list with metadata
 *
 * Caching: ISR revalidation every 600 seconds (10 minutes)
 * - Stale content served while revalidating in background
 *
 * @example
 * const articles = await fetchLatestArticles(7, 50, 1);
 * console.log(articles.total_hits); // Total number of articles
 */
export async function fetchLatestArticles(days: number = 7, pageSize: number = 15, page: number = 1): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '*',  // Wildcard query (all articles)
      filters: {
        published_from: '2020-01-01',  // Wide date range to get all articles
        published_until: '2030-12-31',
        providers: [],    // Empty = all providers
        categories: []    // Empty = all categories
      },
      page: page,
      page_size: pageSize
    }),
    next: { revalidate: 600 }  // ISR: Revalidate every 10 minutes
  });

  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
}

/**
 * Fetch full article details by ID
 *
 * @param articleId - Unique article identifier (format: category.timestamp)
 * @returns Promise<ArticleDetail> - Full article with content
 *
 * Caching: ISR revalidation every 3600 seconds (1 hour)
 *
 * @example
 * const article = await fetchArticleDetail('02100311.20251222092834001');
 */
export async function fetchArticleDetail(articleId: string) {
  const response = await fetch(`${API_URL}/api/article/${articleId}`, {
    next: { revalidate: 3600 }
  });
  if (!response.ok) throw new Error('Failed to fetch article');
  return response.json();
}

/**
 * Fetch article by SEO-friendly slug
 *
 * @param slug - URL slug (e.g., 'samsung-earnings-report')
 * @returns Promise<ArticleDetail> - Full article with content
 *
 * Caching: ISR revalidation every 3600 seconds (1 hour)
 *
 * @example
 * const article = await fetchArticleBySlug('samsung-q4-earnings');
 */
export async function fetchArticleBySlug(slug: string) {
  const response = await fetch(`${API_URL}/api/article/by-slug/${slug}`, {
    next: { revalidate: 3600 }
  });
  if (!response.ok) throw new Error('Failed to fetch article by slug');
  return response.json();
}

/**
 * Fetch articles from a specific category
 *
 * @param category - English category name ('finance', 'technology', etc.)
 * @param page - Page number for pagination (default: 1)
 * @param pageSize - Articles per page (default: 20)
 * @returns Promise<SearchResponse> - Paginated category articles
 *
 * Category Conversion:
 * - Converts English category to Korean for API query
 * - Uses englishToKorean() which returns an array
 * - Example: 'finance' → ['경제'], 'technology' → ['IT_과학']
 *
 * Caching: No ISR (dynamic) - always fresh content
 *
 * @example
 * const finance = await fetchCategoryArticles('finance', 1, 20);
 */
export async function fetchCategoryArticles(category: string, page: number = 1, pageSize: number = 20): Promise<SearchResponse> {
  // Convert English category to Korean for API query
  const koreanCategory = englishToKorean(category);

  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '*',
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        providers: ['서울경제'],
        categories: koreanCategory // englishToKorean returns array, don't wrap again
      },
      page: page,
      page_size: pageSize
    })
  });

  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
}

/**
 * Fetch related articles for an article
 *
 * @param category - English category name for fallback
 * @param articleId - Current article ID to exclude from results
 * @param pageSize - Number of related articles to fetch (default: 4)
 * @returns Promise<CategoryArticle[]> - Related articles
 *
 * Recommendation Strategy:
 * 1. Try hashtag-based recommendations first (AI-powered)
 * 2. Fallback to category-based if hashtag method fails
 * 3. Filter out current article from results
 *
 * Caching: ISR revalidation every 1800 seconds (30 minutes)
 *
 * @example
 * const related = await fetchRelatedArticles('finance', 'abc123', 4);
 */
export async function fetchRelatedArticles(category: string, articleId: string, pageSize: number = 4): Promise<CategoryArticle[]> {
  // Try hashtag-based recommendations first (AI-powered)
  try {
    const response = await fetch(`${API_URL}/api/related/${articleId}?limit=${pageSize}`, {
      next: { revalidate: 1800 }
    });
    if (response.ok) {
      const data = await response.json();
      if (data.related_articles && data.related_articles.length > 0) {
        return data.related_articles;
      }
    }
  } catch (error) {
    console.warn('Hashtag-based recommendations failed, falling back to category-based');
  }

  // Fallback to category-based recommendations
  const REVERSE_CATEGORY_MAP: Record<string, string[]> = {
    'finance': ['경제'],
    'technology': ['IT_과학'],
    'politics': ['정치'],
    'society': ['사회'],
    'culture': ['문화'],
    'sports': ['스포츠'],
    'international': ['국제'],
    'news': []
  };

  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '*',
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        categories: REVERSE_CATEGORY_MAP[category] || []
      },
      page: 1,
      page_size: pageSize
    }),
    next: { revalidate: 1800 }
  });

  if (!response.ok) throw new Error('Failed to fetch related articles');
  const data = await response.json();
  // Filter out current article from results
  return (data.articles || []).filter((a: CategoryArticle) => a.news_id !== articleId);
}

/**
 * Search articles by keyword query
 *
 * @param query - Search keywords
 * @param page - Page number for pagination (default: 1)
 * @param pageSize - Articles per page (default: 20)
 * @returns Promise<SearchResponse> - Paginated search results
 *
 * Search Features:
 * - Full-text search in title and content
 * - Searches across all categories and time periods
 *
 * Caching: ISR revalidation every 300 seconds (5 minutes)
 *
 * @example
 * const results = await searchArticles('Samsung Galaxy', 1, 20);
 */
export async function searchArticles(query: string, page: number = 1, pageSize: number = 20): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        providers: [],    // All providers
        categories: []    // All categories
      },
      page: page,
      page_size: pageSize
    }),
    next: { revalidate: 300 }  // ISR: Revalidate every 5 minutes
  });

  if (!response.ok) throw new Error('Failed to search articles');
  return response.json();
}
