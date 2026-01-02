'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Filter, Calendar, Edit, Trash2, LogOut, Eye, ExternalLink, Info, ArrowUpDown, ArrowUp, ArrowDown, ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight, Settings } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';

interface Article {
  news_id: string;
  title: string;
  title_en?: string;
  category: string;
  published_at: string;
  provider?: string;
  status?: string;
  slug?: string;
}

interface ArticleListResponse {
  articles: Article[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function ArticlesPage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc'); // desc = newest first
  const pageSize = 20;

  useEffect(() => {
    const isAuth = localStorage.getItem('cms_auth');
    if (isAuth !== 'true') {
      router.push('/login');
    } else {
      setIsChecking(false);
    }
  }, [router]);

  useEffect(() => {
    if (!isChecking) {
      fetchArticles();
    }
  }, [currentPage, categoryFilter, sortOrder, isChecking]);

  const handleLogout = () => {
    localStorage.removeItem('cms_auth');
    router.push('/login');
  };

  async function fetchArticles() {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
        sort_order: sortOrder,
      });

      if (categoryFilter !== 'all') {
        params.append('category', categoryFilter);
      }

      const response = await fetch(`${API_URL}/admin/articles?${params}`);
      const data: ArticleListResponse = await response.json();

      setArticles(data.articles || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
    } catch (error) {
      console.error('Failed to fetch articles:', error);
      setArticles([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(newsId: string) {
    if (!confirm('⚠️ Are you sure you want to delete this article? This cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/delete-article`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ news_id: newsId })
      });

      if (response.ok) {
        alert('✅ Article deleted successfully!');
        fetchArticles(); // Refresh list
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      alert('❌ Failed to delete article');
      console.error(error);
    }
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  }

  function buildArticleUrl(article: Article): string {
    // Use slug-based URL if available
    if (article.slug) {
      const dateStr = article.published_at.substring(0, 10);
      const [year, month, day] = dateStr.split('-');
      const categorySlug = getCategorySlugFromKorean(article.category);
      return `https://en.sedaily.com/${categorySlug}/${year}/${month}/${day}/${article.slug}`;
    }
    // Fallback to legacy URL
    return `https://en.sedaily.com/article?id=${article.news_id}`;
  }

  function getCategorySlugFromKorean(category: string): string {
    const categoryMap: Record<string, string> = {
      '경제': 'finance',
      'IT_과학': 'technology',
      '정치': 'politics',
      '사회': 'society',
      '문화': 'culture',
      '스포츠': 'sports',
      '국제': 'international',
      '지역': 'society'  // Regional news goes under Society
    };
    return categoryMap[category] || 'news';
  }

  function getCategoryInEnglish(category: string) {
    const categoryMap: Record<string, string> = {
      '경제': 'Finance',
      'IT_과학': 'Technology',
      '정치': 'Politics',
      '사회': 'Society',
      '문화': 'Culture',
      '스포츠': 'Sports',
      '국제': 'International',
      '지역': 'Regional'  // Display as Regional but routes to society
    };
    return categoryMap[category] || category;
  }

  // Filter articles (no sorting - backend handles it)
  const filteredArticles = articles.filter(article => {
    const titleMatch = (article.title_en || article.title || '').toLowerCase().includes(searchTerm.toLowerCase());
    const idMatch = article.news_id.toLowerCase().includes(searchTerm.toLowerCase());
    return titleMatch || idMatch;
  });

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc');
    setCurrentPage(1); // Reset to first page when changing sort order
  };

  if (isChecking) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">📰 Article Management</h1>
              <p className="text-sm text-gray-600 mt-1">
                Managing <span className="font-semibold text-blue-600">{total.toLocaleString()}</span> published articles
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push('/settings')}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Info className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900">Search & Filter</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by article title or news ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1 ml-1">Try searching for keywords in English titles</p>
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Categories ({total.toLocaleString()} articles)</option>
                <option value="경제">💼 Finance (경제)</option>
                <option value="IT_과학">💻 Technology (IT_과학)</option>
                <option value="정치">🏛️ Politics (정치)</option>
                <option value="사회">👥 Society (사회)</option>
                <option value="문화">🎨 Culture (문화)</option>
                <option value="스포츠">⚽ Sports (스포츠)</option>
                <option value="국제">🌍 International (국제)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1 ml-1">Filter articles by category</p>
            </div>
          </div>
        </div>

        {/* Articles Table */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm p-16 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
            <p className="mt-6 text-lg font-medium text-gray-700">Loading articles...</p>
            <p className="mt-2 text-sm text-gray-500">Please wait while we fetch the latest content</p>
          </div>
        ) : filteredArticles.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-16 text-center">
            <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No articles found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm ? (
                <>No articles match your search "<span className="font-semibold">{searchTerm}</span>"</>
              ) : (
                <>No articles available in this category</>
              )}
            </p>
            <p className="text-sm text-gray-500">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Article Title
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left">
                        <button
                          onClick={toggleSortOrder}
                          className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase tracking-wider hover:text-gray-700 transition-colors"
                        >
                          Published Date
                          {sortOrder === 'desc' ? (
                            <ArrowDown className="w-4 h-4 text-blue-600" />
                          ) : (
                            <ArrowUp className="w-4 h-4 text-blue-600" />
                          )}
                        </button>
                        <p className="text-xs text-gray-400 normal-case font-normal mt-1">
                          {sortOrder === 'desc' ? 'Newest first' : 'Oldest first'}
                        </p>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Website Link
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredArticles.map((article) => {
                      const websiteUrl = buildArticleUrl(article);
                      return (
                        <tr key={article.news_id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <div className="text-sm font-medium text-gray-900 line-clamp-2">
                              {article.title_en || article.title || 'Untitled'}
                            </div>
                            <div className="text-xs text-gray-500 mt-1 font-mono">
                              ID: {article.news_id}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                              {getCategoryInEnglish(article.category)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                            <div className="flex items-center gap-2">
                              <Calendar className="w-4 h-4 text-gray-400" />
                              <span className="font-medium">{formatDate(article.published_at)}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <a
                              href={websiteUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                            >
                              <ExternalLink className="w-4 h-4" />
                              <span className="truncate max-w-xs">View on Website</span>
                            </a>
                            <div className="text-xs text-gray-400 mt-1 truncate max-w-xs">
                              {websiteUrl.replace('https://en.sedaily.com', '')}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => router.push(`/edit?id=${article.news_id}`)}
                                className="text-blue-600 hover:text-blue-900 p-2 hover:bg-blue-50 rounded transition-colors"
                                title="Edit Article"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDelete(article.news_id)}
                                className="text-red-600 hover:text-red-900 p-2 hover:bg-red-50 rounded transition-colors"
                                title="Delete Article"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white rounded-lg shadow-sm px-6 py-4 mt-4 flex items-center justify-between">
                <div className="flex flex-col gap-1">
                  <div className="text-sm text-gray-700">
                    Showing <span className="font-semibold text-blue-600">{(currentPage - 1) * pageSize + 1}</span> to{' '}
                    <span className="font-semibold text-blue-600">
                      {Math.min(currentPage * pageSize, total)}
                    </span>{' '}
                    of <span className="font-semibold text-blue-600">{total.toLocaleString()}</span> articles
                  </div>
                  <div className="text-xs text-gray-500">
                    Page {currentPage} of {totalPages}
                  </div>
                </div>
                <div className="flex gap-2 items-center">
                  {/* First Page Button */}
                  <button
                    onClick={() => setCurrentPage(1)}
                    disabled={currentPage === 1}
                    className="p-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="First page"
                  >
                    <ChevronsLeft className="w-4 h-4" />
                  </button>

                  {/* Previous Button */}
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="p-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Previous page"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>

                  {/* Page Numbers - Show 10 at a time */}
                  <div className="flex gap-1">
                    {Array.from({ length: Math.min(10, totalPages) }, (_, i) => {
                      let pageNum;
                      const maxVisible = 10;

                      if (totalPages <= maxVisible) {
                        // Show all pages if total is less than max
                        pageNum = i + 1;
                      } else if (currentPage <= 5) {
                        // Show first 10 pages when near start
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 4) {
                        // Show last 10 pages when near end
                        pageNum = totalPages - maxVisible + 1 + i;
                      } else {
                        // Show current page in middle
                        pageNum = currentPage - 4 + i;
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => setCurrentPage(pageNum)}
                          className={`min-w-[40px] px-3 py-2 border rounded-lg text-sm font-medium transition-colors ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  {/* Next Button */}
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                    className="p-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Next page"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>

                  {/* Last Page Button */}
                  <button
                    onClick={() => setCurrentPage(totalPages)}
                    disabled={currentPage === totalPages}
                    className="p-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Last page"
                  >
                    <ChevronsRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
