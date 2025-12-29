import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Calendar, User } from "lucide-react";
import { fetchArticleBySlug, fetchRelatedArticles } from "@/utils/api";
import { formatDate } from "@/utils/formatDate";
import { ArticleDetail } from "@/types/article";
import { ArticleImage } from "@/components/article/ArticleImage";
import { getCategoryInEnglish } from "@/utils/categoryUtils";
import { convertByline, getReporterNameInEnglish } from "@/utils/convertByline";
import { buildArticleUrl } from "@/utils/articleUrl";

// ISR: Revalidate every 1 hour (articles rarely change)
export const revalidate = 3600;

// Type for params
interface PageParams {
  category: string;
  year: string;
  month: string;
  day: string;
  slug: string;
}

// Generate dynamic metadata for SEO
export async function generateMetadata({
  params,
}: {
  params: PageParams;
}): Promise<Metadata> {
  try {
    const article = await fetchArticleBySlug(params.slug);

    const canonicalUrl = `https://en.sedaily.com/${params.category}/${params.year}/${params.month}/${params.day}/${params.slug}`;

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
            return cleaned && cleaned.length > 0 && !/^\*+$/.test(cleaned) && /[a-zA-Z가-힣0-9]/.test(cleaned);
          }),
        url: canonicalUrl,
        siteName: "Seoul Economic Daily",
        locale: "en_US",
        images: article.original_link
          ? [
              {
                url: generateImageUrl(
                  article.original_link,
                  article.published_at
                ),
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
        canonical: canonicalUrl,
        languages: {
          'ko': article.original_link || 'https://sedaily.com',
          'en': canonicalUrl,
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

function generateImageUrl(originalLink: string, publishedAt: string): string {
  const date = publishedAt.substring(0, 10).split("-");
  const [year, month, day] = date;
  const code = originalLink.split("/").pop();
  return `https://newsimg.sedaily.com/${year}/${month}/${day}/${code}_1.jpg`;
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
export default async function SlugArticlePage({
  params,
}: {
  params: PageParams;
}) {
  let article: ArticleDetail;

  try {
    article = await fetchArticleBySlug(params.slug);
  } catch (error) {
    console.error("Failed to fetch article:", error);
    notFound();
  }

  // Generate canonical URL
  const canonicalUrl = `https://en.sedaily.com/${params.category}/${params.year}/${params.month}/${params.day}/${params.slug}`;

  // Extract first 2-3 sentences for abstract (GEO: AI crawlers prioritize abstract)
  const getArticleAbstract = (content: string | undefined, metaDesc: string | undefined): string => {
    if (metaDesc) return metaDesc;
    if (!content) return "";

    // Extract first 2-3 sentences (up to 200 chars)
    const sentences = content.match(/[^.!?]+[.!?]+/g) || [];
    let abstract = "";
    for (let i = 0; i < Math.min(3, sentences.length); i++) {
      abstract += sentences[i].trim() + " ";
      if (abstract.length > 200) break;
    }
    return abstract.trim() || content.substring(0, 200);
  };

  // Extract entities from hashtags for better graph RAG indexing
  const extractEntities = (hashtags: string | undefined) => {
    if (!hashtags) return { topics: [], mentions: [] };

    const tags = hashtags
      .split(/[,\s]+/)
      .filter((tag: string) => {
        const cleaned = tag.trim().replace(/^#/, '');
        return cleaned && cleaned.length > 0 && !/^\*+$/.test(cleaned) && /[a-zA-Z가-힣0-9]/.test(cleaned);
      })
      .map((tag: string) => tag.trim().replace(/^#/, ''));

    // First 3 tags as main topics
    const topics = tags.slice(0, 3).map((tag: string) => ({
      "@type": "Thing",
      "name": tag,
    }));

    // Rest as mentions (entities)
    const mentions = tags.slice(3, 8).map((tag: string) => ({
      "@type": "Thing",
      "name": tag,
    }));

    return { topics, mentions };
  };

  const entities = extractEntities(article.hashtags);

  // Generate JSON-LD structured data with ImageObject for better SEO
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    description:
      article.meta_description ||
      article.content?.substring(0, 160) ||
      article.title,

    // GEO Enhancement: abstract (AI crawlers prefer concise summaries)
    abstract: getArticleAbstract(article.content, article.meta_description),

    // GEO Enhancement: articleBody (full content for AI crawlers)
    articleBody: article.content || "",

    datePublished: article.published_at,
    dateModified: article.published_at,

    // Enhanced Author Schema (GEO/AEO: AI crawlers prioritize credible authors)
    author: article.byline
      ? {
          "@type": "Person",
          name: getReporterNameInEnglish(article.byline),
          jobTitle: "Reporter",
          worksFor: {
            "@type": "Organization",
            name: "Seoul Economic Daily",
            url: "https://en.sedaily.com",
          },
          url: "https://en.sedaily.com/about",
        }
      : {
          "@type": "Organization",
          name: "Seoul Economic Daily Editorial Team",
          url: "https://en.sedaily.com",
          logo: {
            "@type": "ImageObject",
            url: "https://en.sedaily.com/sedaily-logo.png",
            width: 600,
            height: 60,
          },
        },

    // Enhanced Publisher Schema
    publisher: {
      "@type": "Organization",
      name: "Seoul Economic Daily",
      url: "https://en.sedaily.com",
      logo: {
        "@type": "ImageObject",
        url: "https://en.sedaily.com/sedaily-logo.png",
        width: 600,
        height: 60,
      },
      sameAs: [
        "https://twitter.com/sedaily_com",
        "https://www.facebook.com/sedaily",
        "https://www.sedaily.com",
      ],
      foundingDate: "1960-05-09",
      address: {
        "@type": "PostalAddress",
        addressCountry: "KR",
        addressLocality: "Seoul",
      },
    },

    image: article.original_link
      ? {
          "@type": "ImageObject",
          url: generateImageUrl(article.original_link, article.published_at),
          caption: `${article.title} - Seoul Economic Daily ${getCategoryInEnglish(article.category)} News from South Korea`,
          contentUrl: generateImageUrl(article.original_link, article.published_at),
          width: 1200,
          height: 630,
        }
      : undefined,

    keywords: article.keywords,
    articleSection: getCategoryInEnglish(article.category),

    // GEO Enhancement: about (main topics - increases chunk information density)
    about: entities.topics.length > 0 ? entities.topics : undefined,

    // GEO Enhancement: mentions (referenced entities - helps graph RAG)
    mentions: entities.mentions.length > 0 ? entities.mentions : undefined,

    inLanguage: "en-US",
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": canonicalUrl,
    },
    url: canonicalUrl,

    // GEO Enhancement: isAccessibleForFree (transparency for AI crawlers)
    isAccessibleForFree: true,
  };

  // BreadcrumbList Schema (GEO/AEO: Helps AI understand content hierarchy)
  const breadcrumbList = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: "https://en.sedaily.com",
      },
      {
        "@type": "ListItem",
        position: 2,
        name: getCategoryInEnglish(article.category),
        item: `https://en.sedaily.com/${params.category}`,
      },
      {
        "@type": "ListItem",
        position: 3,
        name: article.title,
        item: canonicalUrl,
      },
    ],
  };

  return (
    <>
      {/* Hreflang tags for multilingual SEO */}
      <link rel="alternate" hrefLang="ko" href={article.original_link || 'https://sedaily.com'} />
      <link rel="alternate" hrefLang="en" href={canonicalUrl} />
      <link rel="alternate" hrefLang="x-default" href={canonicalUrl} />

      {/* NewsArticle Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        suppressHydrationWarning
      />

      {/* BreadcrumbList Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbList) }}
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

          <h1 className="text-2xl md:text-4xl font-bold text-[var(--color-primary)] mb-4 leading-tight">
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
            imageUrl={generateImageUrl(
              article.original_link,
              article.published_at
            )}
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
                      src={`https://tv.naver.com/embed/${videoId}?autoPlay=true`}
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
          <RelatedArticles category={article.category} currentId={article.news_id} />
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
