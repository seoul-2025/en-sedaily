'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { formatDate } from '@/utils/formatDate';
import { getCategoryInEnglish } from '@/utils/categoryUtils';
import { Search as SearchIcon, Calendar, AlertCircle } from 'lucide-react';
import { searchArticles, CategoryArticle } from '@/utils/api';
import { buildArticleUrl } from '@/utils/articleUrl';

// 이미지 없는 기사용 플레이스홀더
function SearchImagePlaceholder() {
  return (
    <div className="w-48 h-32 flex-shrink-0 bg-white flex items-center justify-center rounded-lg border border-gray-100">
      <img
        src="/sedaily-og-image.png"
        alt="Seoul Economic Daily"
        className="w-36 h-auto"
      />
    </div>
  );
}

// 이미지 로드 실패 시 파비콘 플레이스홀더로 대체하는 컴포넌트
function SearchResultImage({ src, alt }: { src: string; alt: string }) {
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return <SearchImagePlaceholder />;
  }

  return (
    <img
      src={src}
      alt={alt}
      className="w-48 h-32 object-cover flex-shrink-0 rounded-lg"
      onError={() => setHasError(true)}
    />
  );
}

// Wave Dots Loading Animation
function WaveLoader() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="flex items-center gap-2">
        {[0, 1, 2, 3, 4].map((i) => (
          <span
            key={i}
            className="w-3 h-3 bg-[var(--color-accent)] rounded-full animate-bounce"
            style={{
              animationDelay: `${i * 0.1}s`,
              animationDuration: '0.6s',
            }}
          />
        ))}
      </div>
      <p className="mt-4 text-[var(--color-text-muted)] text-sm">Searching...</p>
    </div>
  );
}

function SearchResults() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [articles, setArticles] = useState<CategoryArticle[]>([]);
  const [totalHits, setTotalHits] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const pageSize = 20;

  useEffect(() => {
    if (!query) {
      setArticles([]);
      setTotalHits(0);
      setCurrentPage(1);
      setTotalPages(0);
      return;
    }

    setLoading(true);
    setError('');

    searchArticles(query, currentPage, pageSize)
      .then(data => {
        setArticles(data.articles || []);
        setTotalHits(data.total_hits || 0);
        setTotalPages(data.total_pages || 0);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to search articles. Please try again.');
        setLoading(false);
      });
  }, [query, currentPage]);

  const goToPage = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];
    const maxVisible = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage < maxVisible - 1) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return (
      <div className="flex items-center justify-center gap-2 py-8">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-4 py-2 rounded-lg bg-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-accent)] hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        
        {startPage > 1 && (
          <>
            <button
              onClick={() => goToPage(1)}
              className="px-4 py-2 rounded-lg bg-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-accent)] hover:text-white transition-colors"
            >
              1
            </button>
            {startPage > 2 && <span className="text-[var(--color-text-muted)]">...</span>}
          </>
        )}
        
        {pages.map(page => (
          <button
            key={page}
            onClick={() => goToPage(page)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              page === currentPage
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-accent)] hover:text-white'
            }`}
          >
            {page}
          </button>
        ))}
        
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="text-[var(--color-text-muted)]">...</span>}
            <button
              onClick={() => goToPage(totalPages)}
              className="px-4 py-2 rounded-lg bg-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-accent)] hover:text-white transition-colors"
            >
              {totalPages}
            </button>
          </>
        )}
        
        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-4 py-2 rounded-lg bg-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-accent)] hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    );
  };

  const highlightText = (text: string, searchQuery: string) => {
    if (!searchQuery.trim()) return text;
    const regex = new RegExp(`(${searchQuery})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, i) => 
      regex.test(part) 
        ? <mark key={i} className="bg-yellow-200 px-1 rounded">{part}</mark>
        : part
    );
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Search Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <SearchIcon className="w-8 h-8 text-accent" />
          <h1 className="text-3xl font-bold text-[var(--color-text)]">Search Results</h1>
        </div>
        {query && (
          <p className="text-lg text-[var(--color-text)]">
            Results for: <span className="font-semibold text-[var(--color-text)]">"{query}"</span>
          </p>
        )}
        {!loading && totalHits > 0 && (
          <p className="text-sm text-[var(--color-text)] mt-2">
            Found <span className="font-medium text-[var(--color-text)]">{totalHits}</span> article{totalHits !== 1 ? 's' : ''}
          </p>
        )}
      </header>


      {/* Loading State */}
      {loading && <WaveLoader />}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800 mb-1">Error</h3>
              <p className="text-red-700">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && articles.length === 0 && query && (
        <div className="text-center py-16 bg-gray-50 rounded-lg">
          <SearchIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600 mb-4">We couldn't find any articles matching "{query}"</p>
          <p className="text-sm text-gray-500">Try different keywords or check your spelling</p>
        </div>
      )}

      {/* No Query State */}
      {!query && (
        <div className="text-center py-16 bg-gray-50 rounded-lg">
          <SearchIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Start your search</h3>
          <p className="text-gray-600">Enter keywords in the search bar to find articles</p>
        </div>
      )}

      {/* Results */}
      {!loading && articles.length > 0 && (
        <>
        <div className="space-y-6">
          {articles.map((article) => {
            const articleUrl = buildArticleUrl({
              news_id: article.news_id,
              slug: article.slug,
              published_at: article.published_at,
              category: article.category
            });

            return (
              <article
                key={article.news_id}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-all duration-200 group"
              >
                <Link href={articleUrl} className="block">
                <div className="flex gap-4">
                  {article.original_link && (() => {
                    const date = article.published_at.substring(0, 10).split('-');
                    const [year, month, day] = date;
                    const code = article.original_link.split('/').pop();
                    const imageUrl = `https://newsimg.sedaily.com/${year}/${month}/${day}/${code}_1.jpg`;
                    return (
                      <SearchResultImage src={imageUrl} alt={article.title} />
                    );
                  })()}
                  <div className="flex-1 p-6">
                    <h2 className="text-xl font-semibold text-[var(--color-text)] mb-3 group-hover:text-[var(--color-accent)] transition-colors leading-tight">
                      {highlightText(article.title, query)}
                    </h2>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-[var(--color-text-muted)]">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-[var(--color-accent)]/20 text-[var(--color-accent)] rounded-full font-medium">
                        {getCategoryInEnglish(article.category || 'business')}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        <time dateTime={article.published_at}>
                          {formatDate(article.published_at)}
                        </time>
                      </div>
                      {article.provider && (
                        <span className="text-[var(--color-text-light)]">{article.provider}</span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}
        </div>

        {renderPagination()}
        </>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={null}>
      <SearchResults />
    </Suspense>
  );
}
