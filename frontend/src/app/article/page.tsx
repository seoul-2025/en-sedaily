import { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import Link from "next/link";
import { Calendar, User, AlertCircle } from "lucide-react";
import { fetchArticleDetail, fetchRelatedArticles } from "@/utils/api";
import { formatDate } from "@/utils/formatDate";
import { ArticleDetail } from "@/types/article";
import { ArticleImage } from "@/components/article/ArticleImage";
import { getCategoryInEnglish } from "@/utils/categoryUtils";
import { convertByline, getReporterNameInEnglish } from "@/utils/convertByline";
import { buildArticleUrl } from "@/utils/articleUrl";
import { getImageUrl } from "@/utils/imageUrl";

// Force dynamic rendering for this page
export const dynamic = "force-dynamic";

// Generate dynamic metadata for SEO
export async function generateMetadata({
  searchParams,
}: {
  searchParams: { id?: string };
}): Promise<Metadata> {
  if (!searchParams.id) {
    return {
      title: "Article Not Found - Seoul Economic Daily",
      description: "The requested article could not be found.",
    };
  }

  try {
    const article = await fetchArticleDetail(searchParams.id);

    return {
      title: `${article.title} - Seoul Economic Daily`,
      description:
        article.meta_description ||
        article.content?.substring(0, 160) ||
        article.title,
      keywords: article.keywords,
      authors: [{ name: getReporterNameInEnglish(article.byline || '') }],
      openGraph: {
        title: article.title,
        description:
          article.meta_description ||
          article.content?.substring(0, 160) ||
          article.title,
        type: "article",
        publishedTime: article.published_at,
        authors: [getReporterNameInEnglish(article.byline || '')],
        section: getCategoryInEnglish(article.category),
        tags: article.hashtags
          ?.split(/[,\s]+/)
          .filter((tag: string) => {
            const cleaned = tag.trim().replace(/^#/, '');
            // 빈 태그, ** 같은 잘못된 태그 필터링
            return cleaned && cleaned.length > 0 && !/^\*+$/.test(cleaned) && /[a-zA-Z가-힣0-9]/.test(cleaned);
          }),
        url: `https://en.sedaily.com/article?id=${article.news_id}`,
        siteName: "Seoul Economic Daily",
        locale: "en_US",
        images: article.original_link
          ? [
              {
                url: getImageUrl(article.published_at, article.original_link),
                width: 1200,
                height: 630,
                alt: article.title,
              },
            ]
          : undefined,
      },
      twitter: {
        card: "summary_large_image",
        title: article.title,
        description:
          article.meta_description || article.content?.substring(0, 160),
        site: "@sedaily_com",
        creator: "@sedaily_com",
      },
      alternates: {
        canonical: `https://en.sedaily.com/article?id=${article.news_id}`,
        languages: {
          'ko': article.original_link || 'https://sedaily.com',
          'en': `https://en.sedaily.com/article?id=${article.news_id}`,
        }
      },
    };
  } catch (error) {
    return {
      title: "Article Not Found - Seoul Economic Daily",
      description: "The requested article could not be found.",
    };
  }
}


// Related Articles Component
async function RelatedArticles({
  category,
  currentId,
}: {
  category: string;
  currentId: string;
}) {
  try {
    const related = await fetchRelatedArticles(category, currentId);

    if (related.length === 0) return null;

    return (
      <aside className="mt-12 pt-8 border-t border-[var(--color-border)]">
        <h2 className="font-serif text-2xl font-bold mb-6 text-[var(--color-primary)]">
          Related Articles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {related.slice(0, 3).map((article) => {
            const articleUrl = buildArticleUrl({
              news_id: article.news_id,
              slug: article.slug,
              published_at: article.published_at,
              category: article.category
            });

            return (
              <article
                key={article.news_id}
                className="border-b border-[var(--color-border-light)] pb-4"
              >
                <Link href={articleUrl} className="group block">
                  <h3 className="font-serif text-lg font-bold leading-snug mb-2 text-[var(--color-text)] group-hover:text-[var(--color-accent)] transition-colors">
                    {article.title}
                  </h3>
                  <time className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide">
                    {formatDate(article.published_at)}
                  </time>
                </Link>
              </article>
            );
          })}
        </div>
      </aside>
    );
  } catch (error) {
    console.error("Failed to fetch related articles:", error);
    return null;
  }
}

// Main Article Page Component (Server Component)
export default async function ArticlePage({
  searchParams,
}: {
  searchParams: { id?: string };
}) {
  const articleId = searchParams.id;

  if (!articleId) {
    notFound();
  }

  let article: ArticleDetail;

  try {
    article = await fetchArticleDetail(articleId);
  } catch (error) {
    console.error("Failed to fetch article:", error);
    notFound();
  }

  // 301 Redirect to SEO-friendly URL if slug exists
  // This preserves SEO value and ensures search engines index the new URLs
  const newUrl = buildArticleUrl({
    news_id: article.news_id,
    slug: article.slug,
    published_at: article.published_at,
    category: article.category
  });

  // Redirect to new URL if it's different from legacy format
  if (article.slug && newUrl !== `/article?id=${articleId}`) {
    redirect(newUrl); // 308 Permanent Redirect (Next.js default for redirect)
  }

  // Generate JSON-LD structured data with ImageObject for better SEO
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    description:
      article.meta_description ||
      article.content?.substring(0, 160) ||
      article.title,
    datePublished: article.published_at,
    dateModified: article.published_at,
    author: {
      "@type": article.byline ? "Person" : "Organization",
      name: getReporterNameInEnglish(article.byline || ''),
    },
    publisher: {
      "@type": "Organization",
      name: "Seoul Economic Daily",
      logo: {
        "@type": "ImageObject",
        url: "https://en.sedaily.com/sedaily-logo.png",
        width: 600,
        height: 60,
      },
    },
    image: article.original_link
      ? {
          "@type": "ImageObject",
          url: getImageUrl(article.published_at, article.original_link),
          caption: `${article.title} - Seoul Economic Daily ${getCategoryInEnglish(article.category)} News from South Korea`,
          contentUrl: getImageUrl(article.published_at, article.original_link),
          width: 1200,
          height: 630,
        }
      : undefined,
    keywords: article.keywords,
    articleSection: getCategoryInEnglish(article.category),
    inLanguage: "en-US",
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `https://en.sedaily.com/article?id=${article.news_id}`,
    },
    url: `https://en.sedaily.com/article?id=${article.news_id}`,
  };

  const legacyUrl = `https://en.sedaily.com/article?id=${article.news_id}`;

  return (
    <>
      {/* Hreflang tags for multilingual SEO */}
      <link rel="alternate" hrefLang="ko" href={article.original_link || 'https://sedaily.com'} />
      <link rel="alternate" hrefLang="en" href={legacyUrl} />
      <link rel="alternate" hrefLang="x-default" href={newUrl} />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        suppressHydrationWarning
      />

      <article className="max-w-3xl mx-auto py-8 px-gutter md:px-gutter-md">
        <header className="mb-8">
          <div className="flex items-center gap-4 text-sm text-[var(--color-text-light)] mb-4">
            <span className="px-3 py-1 bg-accent/20 text-[var(--color-accent)] rounded-full font-medium">
              {getCategoryInEnglish(article.category)}
            </span>
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <time dateTime={article.published_at}>
                {formatDate(article.published_at)}
              </time>
            </div>
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-[var(--color-primary)] mb-4 leading-tight">
            {article.title}
          </h1>

          <div className="flex items-center gap-2 text-[var(--color-text-light)]">
            <User className="w-4 h-4" />
            <span className="font-medium">{convertByline(article.byline || '')}</span>
          </div>

          {article.hashtags && (
            <div className="flex gap-2 flex-wrap mt-3">
              {article.hashtags
                .split(/[,\s]+/)
                .filter((tag: string) => {
                  const cleaned = tag.trim().replace(/^#/, '');
                  // 빈 태그, ** 같은 잘못된 태그 필터링
                  return cleaned && cleaned.length > 0 && !/^\*+$/.test(cleaned) && /[a-zA-Z가-힣0-9]/.test(cleaned);
                })
                .map((tag: string, i: number) => {
                  const cleanTag = tag.trim().replace(/^#/, "");
                  return (
                    <Link
                      key={i}
                      href={`/search?q=${encodeURIComponent(cleanTag)}`}
                      className="text-sm px-2 py-1 bg-[var(--color-accent)]/10 text-[var(--color-accent)] rounded hover:bg-[var(--color-accent)]/20 transition-colors cursor-pointer"
                    >
                      #{cleanTag}
                    </Link>
                  );
                })}
            </div>
          )}
        </header>

        {article.original_link && (
          <ArticleImage
            imageUrl={getImageUrl(article.published_at, article.original_link)}
            title={article.title}
            category={getCategoryInEnglish(article.category)}
            originalLink={article.original_link}
          />
        )}

        <div className="prose prose-lg max-w-none">
          {article.content ? (
            article.content.split("\n").map(
              (paragraph: string, idx: number) =>
                paragraph.trim() && (
                  <p
                    key={idx}
                    className="mb-4 text-[var(--color-text)] leading-relaxed"
                  >
                    {paragraph}
                  </p>
                )
            )
          ) : (
            <p className="text-gray-500 italic">
              Content not available. Please visit the original article.
            </p>
          )}
        </div>

        {/* Naver TV Video Player */}
        {article.naver_tv_url &&
          (() => {
            const videoId = article.naver_tv_url.match(/\/v\/(\d+)/)?.[1];
            if (videoId) {
              return (
                <div className="mt-8 mb-8">
                  <h3 className="text-xl font-bold mb-4 text-[var(--color-primary)]">
                    Related Video
                  </h3>
                  <div
                    className="relative"
                    style={{ paddingBottom: "56.25%", height: 0 }}
                  >
                    <iframe
                      src={`https://tv.naver.com/embed/${videoId}?autoPlay=false`}
                      className="absolute top-0 left-0 w-full h-full rounded-lg"
                      frameBorder="0"
                      allow="autoplay; fullscreen"
                      allowFullScreen
                    />
                  </div>
                </div>
              );
            }
            return null;
          })()}

        {article.original_link && (
          <footer className="mt-12 pt-6 border-t border-gray-200 dark:border-gray-700">
            <a
              href={article.original_link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline text-sm"
            >
              View original article →
            </a>
          </footer>
        )}

        {/* Related Articles Section */}
        {article.category && (
          <RelatedArticles category={article.category} currentId={articleId} />
        )}

        <div className="mt-8">
          <Link href="/" className="text-accent hover:underline">
            ← Back to Home
          </Link>
        </div>
      </article>
    </>
  );
}
