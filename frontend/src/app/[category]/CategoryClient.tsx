'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { formatDate, formatRelativeTime } from '@/utils/formatDate';
import { fetchCategoryArticles, CategoryArticle } from '@/utils/api';
import { Clock } from 'lucide-react';
import { convertByline } from '@/utils/convertByline';
import { buildArticleUrl } from '@/utils/articleUrl';
import { getImageUrl } from '@/utils/imageUrl';

// 이미지 로드 실패 시 로고 플레이스홀더로 대체하는 컴포넌트
function HeroImage({ src, alt, category }: { src: string; alt: string; category?: string }) {
  const [hasError, setHasError] = useState(false);

  // SEO-optimized alt text with category information
  const seoAlt = category
    ? `${alt} - Seoul Economic Daily ${category} News from South Korea`
    : `${alt} - Seoul Economic Daily News from South Korea`;

  if (hasError) {
    return (
      <div className="w-full h-96 bg-white flex items-center justify-center rounded-lg mb-6 border border-gray-100">
        <Image
          src="/sedaily-og-image.png"
          alt="Seoul Economic Daily - English News from South Korea"
          width={320}
          height={180}
          className="w-80 h-auto"
          priority
        />
      </div>
    );
  }

  return (
    <div className="relative w-full h-96 rounded-lg overflow-hidden mb-6">
      <Image
        src={src}
        alt={seoAlt}
        title={alt}
        fill
        className="object-cover"
        sizes="(max-width: 768px) 100vw, 1200px"
        priority
        onError={() => setHasError(true)}
      />
    </div>
  );
}

// 썸네일 이미지 컴포넌트
function ThumbnailImage({ src, alt, category }: { src: string; alt: string; category?: string }) {
  const [hasError, setHasError] = useState(false);

  // SEO-optimized alt text with category information
  const seoAlt = category
    ? `${alt} - Seoul Economic Daily ${category} News from South Korea`
    : `${alt} - Seoul Economic Daily News from South Korea`;

  if (hasError) {
    return <ThumbnailPlaceholder />;
  }

  return (
    <div className="relative w-40 h-28 md:w-48 md:h-32 flex-shrink-0 rounded-lg overflow-hidden">
      <Image
        src={src}
        alt={seoAlt}
        title={alt}
        fill
        className="object-cover"
        sizes="(max-width: 768px) 160px, 192px"
        onError={() => setHasError(true)}
      />
    </div>
  );
}

// 이미지 없는 기사용 플레이스홀더
function ThumbnailPlaceholder() {
  return (
    <div className="w-40 h-28 md:w-48 md:h-32 flex-shrink-0 bg-white flex items-center justify-center rounded-lg border border-gray-100">
      <Image
        src="/sedaily-og-image.png"
        alt="Seoul Economic Daily - English News from South Korea"
        width={144}
        height={81}
        className="w-32 md:w-36 h-auto"
      />
    </div>
  );
}

interface Props {
  category: string;
  config: { title: string; description: string; color: string };
  initialArticles: CategoryArticle[];
  totalHits: number;
}

export function CategoryClient({ category, config, initialArticles, totalHits }: Props) {
  const [articles, setArticles] = useState<CategoryArticle[]>(initialArticles);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(totalHits > 15);
  const [loadingMore, setLoadingMore] = useState(false);

  const loadMore = async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const data = await fetchCategoryArticles(category, nextPage, 10);
      const newArticles = data.articles || [];
      setArticles(prev => [...prev, ...newArticles]);
      setPage(nextPage);
      setHasMore(data.total_hits > nextPage * 10);
    } catch (error) {
      console.error('Failed to load more articles:', error);
    } finally {
      setLoadingMore(false);
    }
  };

  if (articles.length === 0) {
    return (
      <div className="text-center py-16">
        <h3 className="text-xl font-semibold text-[var(--color-text)] mb-2">No articles available</h3>
        <p className="text-[var(--color-text-light)]\">Check back later for new {category} articles</p>
      </div>
    );
  }

  // 이미지가 있는 기사(original_link 존재)를 우선적으로 Hero로 선택
  const heroArticle = articles.find(a => a.original_link) || articles[0];
  const otherArticles = articles.filter(a => a.news_id !== heroArticle?.news_id);

  return (
    <>
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Main Content */}
      <div className="lg:col-span-8 space-y-8">
        {/* Hero Article */}
        {heroArticle && (() => {
          const heroUrl = buildArticleUrl({
            news_id: heroArticle.news_id,
            slug: heroArticle.slug,
            published_at: heroArticle.published_at,
            category: heroArticle.category
          });

          return (
            <article className="border-b border-[var(--color-border)] pb-8">
              <Link href={heroUrl} className="group block">
              {heroArticle.original_link && (
                <HeroImage
                  src={getImageUrl(heroArticle.published_at, heroArticle.original_link)}
                  alt={heroArticle.title}
                  category={config.title}
                />
              )}
              <h2 className="font-serif text-4xl font-bold leading-tight mb-4 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                {heroArticle.title}
              </h2>
              <div className="flex items-center gap-3 text-sm text-[var(--color-text-muted)]">
                <time dateTime={heroArticle.published_at}>
                  {formatDate(heroArticle.published_at)}
                </time>
              </div>
            </Link>
          </article>
        );
      })()}

        {/* Article List with Thumbnails */}
        <div className="space-y-6">
          {otherArticles.map((article) => {
            const articleUrl = buildArticleUrl({
              news_id: article.news_id,
              slug: article.slug,
              published_at: article.published_at,
              category: article.category
            });

            return (
              <article key={article.news_id} className="border-b border-[var(--color-border)] pb-6 last:border-0">
                <Link href={articleUrl} className="group flex gap-4">
                {/* Thumbnail */}
                {article.original_link ? (
                  <ThumbnailImage
                    src={getImageUrl(article.published_at, article.original_link)}
                    alt={article.title}
                    category={config.title}
                  />
                ) : (
                  <ThumbnailPlaceholder />
                )}
                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-serif text-lg md:text-xl font-bold leading-tight mb-2 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors line-clamp-2">
                    {article.title}
                  </h3>
                  {(article.content || article.meta_description) && (
                    <p className="text-sm text-[var(--color-text-light)] line-clamp-2 mb-3 hidden md:block">
                      {(article.meta_description || article.content || '').substring(0, 150)}...
                    </p>
                  )}
                  <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)]">
                    <Clock className="w-3 h-3" />
                    <time dateTime={article.published_at}>
                      {formatRelativeTime(article.published_at)}
                    </time>
                    <span className="text-[var(--color-border)]">|</span>
                    <span>
                      {article.byline
                        ? convertByline(article.byline).replace('By ', '')
                        : 'Seoul Economic Daily'}
                    </span>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}
        </div>
      </div>

      {/* Sidebar */}
      <aside className="lg:col-span-4 space-y-8">
        <div className="border-t border-[var(--color-border)] pt-6">
          <h3 className="font-serif text-xl font-bold mb-6 text-[var(--color-primary)]">
            Most Read News
          </h3>
          <ol className="space-y-4">
            {otherArticles.slice(0, 5).map((article, index: number) => {
              const sidebarUrl = buildArticleUrl({
                news_id: article.news_id,
                slug: article.slug,
                published_at: article.published_at,
                category: article.category
              });

              return (
                <li key={article.news_id} className="flex gap-4 border-b border-[var(--color-border-light)] pb-4 last:border-0">
                  <span className="font-serif text-2xl font-bold text-[var(--color-text-muted)] leading-none pt-1">
                    {index + 1}
                  </span>
                  <Link href={sidebarUrl} className="group flex-1">
                  <h4 className="font-sans text-sm leading-snug text-[var(--color-text)] group-hover:text-[var(--color-accent)] transition-colors line-clamp-2">
                    {article.title}
                  </h4>
                </Link>
              </li>
            );
          })}
          </ol>
        </div>
      </aside>
    </div>
    
    {hasMore && (
      <div className="text-center py-12">
        <button
          onClick={loadMore}
          disabled={loadingMore}
          className="px-8 py-3 bg-[var(--color-accent)] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loadingMore ? 'Loading...' : 'Load More Articles'}
        </button>
      </div>
    )}
    </>
  );
}
