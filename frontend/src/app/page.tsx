import { HeroSection } from "@/components/home/HeroSection/HeroSection";
import { Newsletter } from "@/components/home/Newsletter/Newsletter";
import { FeaturedArticle, Article } from "@/types/article";
import { CATEGORY_MAP } from "@/constants/categories";

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
    if (error instanceof Error) {
      console.error("❌ 기사 API 오류:", error.message);
    } else {
      console.error("❌ 기사 API 알 수 없는 오류:", error);
    }
    articles = [];
  }



  // 이미지가 있는 기사(original_link 존재)를 우선적으로 Featured로 선택
  const articleWithImage = articles.find((a: Article) => a.original_link);
  const featuredArticle = articleWithImage || articles[0];

  // Featured로 선택된 기사를 제외한 나머지 기사들
  const remainingArticles = articles.filter((a: Article) => a.id !== featuredArticle?.id);

  const featured: FeaturedArticle | null =
    featuredArticle
      ? {
          ...featuredArticle,
          featured: true,
          subtitle: featuredArticle.content || featuredArticle.title,
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
    <main role="main" className="max-w-container mx-auto px-gutter py-12">
      {featured && (
        <HeroSection
          featured={featured}
          popular={popular}
          articleList={articleList}
        />
      )}
      <Newsletter />
    </main>
  );
}
