export type Category =
  | "finance"
  | "technology"
  | "politics"
  | "society"
  | "culture"
  | "sports"
  | "international"
  | "regional"
  | "industry"
  | "realestate"
  | "news";

// Base interface for all articles (matches backend API response)
export interface BaseArticle {
  news_id: string;
  title: string;
  published_at: string;
  category: string;
  slug?: string;
  original_link?: string;
}

// Article for list/card displays (category pages, search, etc.)
export interface CategoryArticle extends BaseArticle {
  provider?: string;
  content?: string;
  byline?: string;
  meta_description?: string;
}

// Full article detail (article page)
export interface ArticleDetail extends BaseArticle {
  content: string;
  provider: string;
  byline?: string;
  images?: string[];
  images_caption?: string[];
  meta_description?: string;
  keywords?: string;
  hashtags?: string;
  naver_tv_url?: string;
}

// Legacy Article interface for home page components (uses different naming)
export interface Article {
  id: string;
  title: string;
  subtitle?: string;
  summary?: string;
  content?: string;
  category: Category;
  publishedAt: string;
  author?: string;
  url: string;
  original_link?: string;
  slug?: string;
}

export interface FeaturedArticle extends Article {
  featured: true;
}

export interface SearchResponse {
  total_hits: number;
  page: number;
  page_size: number;
  total_pages: number;
  articles: Article[];
}

export interface SectionCardProps {
  title: string;
  articles: Article[];
  showThumbnail?: boolean;
  maxItems?: number;
}
