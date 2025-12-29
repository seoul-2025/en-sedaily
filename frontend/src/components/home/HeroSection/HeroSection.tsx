'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { FeaturedArticle, Article } from '@/types/article';
import { getImageUrl } from '@/utils/imageUrl';

// 히어로 이미지 컴포넌트 (큰 사이즈)
function HeroImage({ src, alt }: { src: string; alt: string }) {
  const [hasError, setHasError] = useState(false);

  // SEO-optimized alt text for featured articles
  const seoAlt = `${alt} - Seoul Economic Daily Featured News from South Korea`;

  if (hasError) {
    return (
      <div className="w-full h-48 md:h-56 bg-white flex items-center justify-center rounded border border-gray-100">
        <Image
          src="/sedaily-og-image.png"
          alt="Seoul Economic Daily - English News from South Korea"
          width={160}
          height={90}
          className="w-40 h-auto"
          priority
        />
      </div>
    );
  }

  return (
    <div className="relative w-full h-48 md:h-56 rounded overflow-hidden">
      <Image
        src={src}
        alt={seoAlt}
        title={alt}
        fill
        className="object-cover"
        sizes="(max-width: 768px) 100vw, 50vw"
        priority
        onError={() => setHasError(true)}
      />
    </div>
  );
}

// 썸네일 이미지 컴포넌트 (작은 사이즈)
function ThumbnailImage({ src, alt }: { src: string; alt: string }) {
  const [hasError, setHasError] = useState(false);

  // SEO-optimized alt text for article thumbnails
  const seoAlt = `${alt} - Seoul Economic Daily News from South Korea`;

  if (hasError) {
    return (
      <div className="w-28 h-20 md:w-36 md:h-24 flex-shrink-0 bg-white flex items-center justify-center rounded border border-gray-100">
        <Image
          src="/sedaily-og-image.png"
          alt="Seoul Economic Daily - English News from South Korea"
          width={80}
          height={45}
          className="w-20 h-auto"
        />
      </div>
    );
  }

  return (
    <div className="relative w-28 h-20 md:w-36 md:h-24 flex-shrink-0 rounded overflow-hidden">
      <Image
        src={src}
        alt={seoAlt}
        title={alt}
        fill
        className="object-cover"
        sizes="(max-width: 768px) 112px, 144px"
        onError={() => setHasError(true)}
      />
    </div>
  );
}

interface Props {
  featured: FeaturedArticle;
  articleList: Article[];
  popular: Article[];
}

export function HeroSection({ featured, articleList, popular }: Props) {
  return (
    <section className="pb-8 mb-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 왼쪽: Featured + Article List */}
        <div className="lg:col-span-2">
          {/* Featured Article (상단 큰 기사) */}
          <article className="mb-8 pb-8 border-b border-[var(--color-border)]">
            <Link href={featured.url} className="group">
              {/* 제목 (상단) */}
              <h1 className="text-2xl md:text-3xl font-bold leading-tight mb-4 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                {featured.title}
              </h1>

              {/* 이미지 + 설명 (가로 배치) */}
              <div className="flex flex-col md:flex-row gap-5">
                <div className="md:w-2/5 flex-shrink-0">
                  {featured.original_link ? (
                    <HeroImage
                      src={getImageUrl(featured.publishedAt, featured.original_link)}
                      alt={featured.title}
                    />
                  ) : (
                    <div className="w-full h-48 md:h-56 bg-white flex items-center justify-center rounded border border-gray-100">
                      <img src="/sedaily-og-image.png" alt="Seoul Economic Daily" className="w-40 h-auto" />
                    </div>
                  )}
                </div>
                <div className="md:w-3/5">
                  <p className="text-sm md:text-base text-[var(--color-text-light)] leading-relaxed line-clamp-5">
                    {featured.subtitle}
                  </p>
                </div>
              </div>
            </Link>

            {/* 관련 기사 링크 (↳) */}
            {articleList.length >= 2 && (
              <div className="mt-4 space-y-2">
                {articleList.slice(0, 2).map((related) => (
                  <Link
                    key={related.id}
                    href={related.url}
                    className="flex items-start gap-2 text-sm text-[var(--color-text)] hover:text-[var(--color-accent)] transition-colors"
                  >
                    <span className="text-[var(--color-text-muted)]">↳</span>
                    <span className="line-clamp-1">{related.title}</span>
                  </Link>
                ))}
              </div>
            )}
          </article>

          {/* Article List (기사 리스트) */}
          <div className="space-y-6">
            {articleList.slice(2).map((article, index) => (
              <article
                key={article.id}
                className={`pb-6 ${index < articleList.length - 3 ? 'border-b border-[var(--color-border)]' : ''}`}
              >
                <Link href={article.url} className="group">
                  {/* 제목 */}
                  <h2 className="text-lg md:text-xl font-bold leading-tight mb-3 text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                    {article.title}
                  </h2>

                  {/* 썸네일 + 본문 미리보기 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      {article.original_link ? (
                        <ThumbnailImage
                          src={getImageUrl(article.publishedAt, article.original_link)}
                          alt={article.title}
                        />
                      ) : (
                        <div className="w-28 h-20 md:w-36 md:h-24 bg-white flex items-center justify-center rounded border border-gray-100">
                          <img src="/sedaily-og-image.png" alt="Seoul Economic Daily" className="w-20 h-auto" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-[var(--color-text-light)] leading-relaxed line-clamp-4">
                        {article.content || article.title}
                      </p>
                    </div>
                  </div>
                </Link>

                {/* 관련 기사 링크 (↳) - 다음 2개 기사 */}
                {index < articleList.length - 4 && (
                  <div className="mt-3 space-y-1.5 pl-1">
                    {articleList.slice(index + 3, index + 5).map((related) => (
                      <Link
                        key={related.id}
                        href={related.url}
                        className="flex items-start gap-2 text-sm text-[var(--color-text)] hover:text-[var(--color-accent)] transition-colors"
                      >
                        <span className="text-[var(--color-text-muted)]">↳</span>
                        <span className="line-clamp-1">{related.title}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </article>
            ))}
          </div>
        </div>

        {/* 오른쪽: 랭킹뉴스 */}
        <div className="lg:col-span-1">
          <div className="sticky top-4">
            <h3 className="font-bold text-lg mb-4 pb-2 border-b-2 border-[var(--color-accent)] text-[var(--color-primary)]">
              Ranking News
            </h3>
            <ol className="space-y-3">
              {popular.slice(0, 10).map((article, index) => (
                <li
                  key={article.id}
                  className="flex gap-3 items-start pb-3 border-b border-[var(--color-border-light)] last:border-0"
                >
                  <span
                    className={`font-bold text-base w-6 flex-shrink-0 ${
                      index < 3 ? 'text-[var(--color-accent)]' : 'text-[var(--color-text-muted)]'
                    }`}
                  >
                    {index + 1}
                  </span>
                  <Link href={article.url} className="group flex-1">
                    <h4 className="text-sm leading-snug text-[var(--color-text)] group-hover:text-[var(--color-accent)] transition-colors line-clamp-2">
                      {article.title}
                    </h4>
                  </Link>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </section>
  );
}
