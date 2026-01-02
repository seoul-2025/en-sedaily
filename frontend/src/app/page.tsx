import { HeroSection } from "@/components/home/HeroSection/HeroSection";
import { Newsletter } from "@/components/home/Newsletter/Newsletter";
import { AdLeaderboard } from "@/components/ads/AdBanner";
import { FeaturedArticle, Article } from "@/types/article";
import { CATEGORY_MAP } from "@/constants/categories";
import { StickyVideoPlayer } from "@/components/video/StickyVideoPlayer";

import { fetchLatestArticles as apifetchLatestArticles } from "@/utils/api";
import { buildArticleUrl } from "@/utils/articleUrl";

// ISR: Revalidate every 60 seconds for fresh content
export const revalidate = 60;

function transformArticle(article: any): Article {
  const category = CATEGORY_MAP[article.category] || "news";

  // Build SEO-friendly URL
  const url = buildArticleUrl({
    news_id: article.news_id,
    slug: article.slug,
    published_at: article.published_at,
    category: article.category
  });

  return {
    id: article.news_id,
    title: article.title,
    content: article.content || article.meta_description || "",
    category,
    publishedAt: article.published_at,
    url,
    original_link: article.original_link,
  };
}

export default async function Home() {
  // Server-side data fetching
  console.log("🔄 Fetching articles...");
  let articles: Article[] = [];

  try {
    const data = await apifetchLatestArticles(30, 50, 1);  // 30일간, 50개로 증가
    console.log("✅ API response:", {
      total: data.total_hits,
      count: data.articles?.length || 0,
    });
    articles = data.articles?.map(transformArticle) || [];
  } catch (error) {
    console.error("❌ API error:", error);
    articles = [];
  }

  // 이미지가 있는 기사(original_link 존재)를 우선적으로 Featured로 선택
  const articlesWithImage = articles.filter((a: Article) => a.original_link);
  
  // 웹용 4개 featured 기사 (이미지 우선)
  const webFeaturedArticles = articlesWithImage.slice(0, 4).length >= 4 
    ? articlesWithImage.slice(0, 4)
    : [...articlesWithImage, ...articles.filter(a => !a.original_link)].slice(0, 4);
  
  // 모바일용 1개 featured 기사 (기존 로직)
  const articleWithImage = articles.find((a: Article) => a.original_link);
  const mobileFeaturedArticle = articleWithImage || articles[0];

  // Featured로 선택된 기사들을 제외한 나머지 기사들 (웹 기준)
  const webFeaturedIds = webFeaturedArticles.map(a => a.id);
  const remainingArticles = articles.filter((a: Article) => !webFeaturedIds.includes(a.id));

  // 웹용 featured 배열
  const webFeatured: FeaturedArticle[] = webFeaturedArticles.map(article => ({
    ...article,
    featured: true,
    subtitle: article.content || article.title,
  }));
  
  // 모바일용 featured 객체 (기존 로직)
  const mobileFeatured: FeaturedArticle | null = mobileFeaturedArticle
    ? {
        ...mobileFeaturedArticle,
        featured: true,
        subtitle: mobileFeaturedArticle.content || mobileFeaturedArticle.title,
      }
    : null;

  // 왼쪽 기사 리스트용 (featured 제외한 나머지) - 15개로 증가
  const articleList = remainingArticles.slice(0, 15);
  // 오른쪽 랭킹뉴스용 - 15개로 증가
  const popular = remainingArticles.slice(15, 30);

  if (articles.length === 0) {
    return (
      <div className="container mx-auto px-gutter py-12 text-center">
        <p className="text-[var(--color-text-light)]">
          No articles available at the moment.
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Ad: Top of Homepage */}
      <AdLeaderboard adSlot="8196460228" className="mb-5" />

      {/* 모바일: 기존 1개 featured, 웹: 4개 featured */}
      {mobileFeatured && (
        <div className="md:hidden">
          <HeroSection
            featured={mobileFeatured}
            popular={popular}
            articleList={articleList}
          />
        </div>
      )}
      
      {webFeatured.length > 0 && (
        <div className="hidden md:block">
          <HeroSection
            featured={webFeatured}
            popular={popular}
            articleList={articleList}
          />
        </div>
      )}

      {/* Sticky Video Player - always visible in bottom-right corner */}
      <StickyVideoPlayer
        videoUrl="https://tv.naver.com/v/91416558"
        alwaysVisible={true}
      />

      <Newsletter />

      {/* Ad: Bottom of Homepage */}
      <AdLeaderboard adSlot="1415413545" className="mt-12" />
    </>
  );
}
