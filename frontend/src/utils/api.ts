import { CategoryArticle, ArticleDetail } from "@/types/article";
import { englishToKorean } from "@/constants/categoryMapping";

export const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

// Re-export for backwards compatibility
export type { CategoryArticle };

export interface SearchResponse {
  articles: CategoryArticle[];
  total_hits: number;
  total_pages: number;
  page: number;
  page_size: number;
}

export async function fetchLatestArticles(days: number = 7, pageSize: number = 15, page: number = 1): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '*',
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        providers: [],
        categories: []
      },
      page: page,
      page_size: pageSize
    }),
    next: { revalidate: 600 }
  });

  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
}

export async function fetchArticleDetail(articleId: string) {
  const response = await fetch(`${API_URL}/api/article/${articleId}`, {
    next: { revalidate: 3600 }
  });
  if (!response.ok) throw new Error('Failed to fetch article');
  return response.json();
}

export async function fetchArticleBySlug(slug: string) {
  const response = await fetch(`${API_URL}/api/article/by-slug/${slug}`, {
    next: { revalidate: 3600 }
  });
  if (!response.ok) throw new Error('Failed to fetch article by slug');
  return response.json();
}

export async function fetchCategoryArticles(category: string, page: number = 1, pageSize: number = 20): Promise<SearchResponse> {
  // Convert English category to Korean categories array for API query
  const koreanCategories = englishToKorean(category);
  console.log(`[DEBUG] Category: ${category}, Korean categories:`, koreanCategories);

  // If multiple subcategories, fetch from each and combine
  if (koreanCategories.length > 1) {
    console.log(`[DEBUG] Multiple categories detected, fetching from ${koreanCategories.length} sources`);
    const allArticles: CategoryArticle[] = [];
    let totalHits = 0;

    // Fetch from each subcategory
    for (const koreanCategory of koreanCategories) {
      try {
        console.log(`[DEBUG] Fetching from category: ${koreanCategory}`);
        const response = await fetch(`${API_URL}/api/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: '*',
            filters: {
              published_from: '2020-01-01',
              published_until: '2030-12-31',
              providers: ['서울경제'],
              categories: [koreanCategory]
            },
            page: 1,
            page_size: Math.ceil(pageSize / koreanCategories.length) + 5 // Get extra to ensure enough articles
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log(`[DEBUG] ${koreanCategory} returned ${data.articles?.length || 0} articles`);
          allArticles.push(...(data.articles || []));
          totalHits += data.total_hits || 0;
        } else {
          console.error(`[DEBUG] Failed to fetch ${koreanCategory}:`, response.status, response.statusText);
        }
      } catch (error) {
        console.warn(`Failed to fetch from category ${koreanCategory}:`, error);
      }
    }

    console.log(`[DEBUG] Combined ${allArticles.length} articles from all sources`);

    // Sort by published_at (newest first) and paginate
    const sortedArticles = allArticles
      .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
      .slice((page - 1) * pageSize, page * pageSize);

    return {
      articles: sortedArticles,
      total_hits: totalHits,
      total_pages: Math.ceil(totalHits / pageSize),
      page,
      page_size: pageSize
    };
  }

  // Single category - use existing logic
  console.log(`[DEBUG] Single category: ${koreanCategories[0]}`);
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: '*',
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        providers: ['서울경제'],
        categories: koreanCategories
      },
      page: page,
      page_size: pageSize
    })
  });

  if (!response.ok) {
    console.error(`[DEBUG] Single category fetch failed:`, response.status, response.statusText);
    throw new Error('Failed to fetch articles');
  }
  const data = await response.json();
  console.log(`[DEBUG] Single category returned ${data.articles?.length || 0} articles`);
  return data;
}

export async function fetchRelatedArticles(category: string, articleId: string, pageSize: number = 4): Promise<CategoryArticle[]> {
  // Try hashtag-based recommendations first
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
  return (data.articles || []).filter((a: CategoryArticle) => a.news_id !== articleId);
}

export async function searchArticles(query: string, page: number = 1, pageSize: number = 20): Promise<SearchResponse> {
  const response = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      filters: {
        published_from: '2020-01-01',
        published_until: '2030-12-31',
        providers: [],
        categories: []
      },
      page: page,
      page_size: pageSize
    }),
    next: { revalidate: 300 }
  });

  if (!response.ok) throw new Error('Failed to search articles');
  return response.json();
}
