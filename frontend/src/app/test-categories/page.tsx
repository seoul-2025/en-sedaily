'use client';

import { useState } from 'react';

const TEST_CATEGORIES = [
  '경제',
  '경제>증권_증시',
  '경제>부동산', 
  '경제>금융_재테크',
  '경제>무역',
  '경제>외환',
  '경제>산업_기업',
  '경제>반도체',
  '경제>유통',
  'IT_과학',
  '정치',
  '사회',
  '문화',
  '스포츠',
  '국제'
];

export default function TestCategoriesPage() {
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  const testAllCategories = async () => {
    setLoading(true);
    const newResults: Record<string, any> = {};

    for (const category of TEST_CATEGORIES) {
      try {
        console.log(`Testing category: ${category}`);
        const response = await fetch('https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev/api/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: '*',
            filters: {
              categories: [category],
              published_from: '2025-12-01',
              published_until: '2025-12-31',
            },
            page: 1,
            page_size: 5,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          newResults[category] = {
            status: 'success',
            total_hits: data.total_hits || 0,
            articles_count: data.articles?.length || 0,
            sample_titles: data.articles?.slice(0, 3).map((a: any) => a.title) || []
          };
        } else {
          newResults[category] = {
            status: 'error',
            error: `HTTP ${response.status}`,
            total_hits: 0
          };
        }
      } catch (error) {
        newResults[category] = {
          status: 'error',
          error: error instanceof Error ? error.message : 'Unknown error',
          total_hits: 0
        };
      }
    }

    setResults(newResults);
    setLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">카테고리별 API 테스트</h1>
      
      <button
        onClick={testAllCategories}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 mb-6"
      >
        {loading ? '테스트 중...' : '모든 카테고리 테스트'}
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {TEST_CATEGORIES.map((category) => {
          const result = results[category];
          return (
            <div key={category} className="border rounded-lg p-4">
              <h3 className="font-bold text-lg mb-2">{category}</h3>
              {result ? (
                <div>
                  <div className={`text-sm mb-2 ${
                    result.status === 'success' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    상태: {result.status}
                  </div>
                  <div className="text-sm mb-2">
                    총 기사 수: <span className="font-bold">{result.total_hits}</span>
                  </div>
                  {result.sample_titles && result.sample_titles.length > 0 && (
                    <div className="text-xs">
                      <div className="font-semibold mb-1">샘플 제목:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {result.sample_titles.map((title: string, idx: number) => (
                          <li key={idx} className="truncate">{title}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {result.error && (
                    <div className="text-red-500 text-xs mt-2">
                      에러: {result.error}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">테스트 대기 중...</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}