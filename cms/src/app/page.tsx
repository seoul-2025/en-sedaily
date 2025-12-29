'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, LogOut } from 'lucide-react';

export default function Home() {
  const [newsId, setNewsId] = useState('');
  const [isChecking, setIsChecking] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const isAuth = localStorage.getItem('cms_auth');
    if (isAuth !== 'true') {
      router.push('/login');
    } else {
      // Redirect to articles page
      router.push('/articles');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('cms_auth');
    router.push('/login');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newsId.trim()) {
      router.push(`/edit?id=${newsId.trim()}`);
    }
  };

  if (isChecking) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-end mb-4">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold mb-2 text-center">Article Editor</h1>
          <p className="text-gray-600 mb-8 text-center">Enter a news ID to edit an article</p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="newsId" className="block text-sm font-medium text-gray-700 mb-2">
                News ID
              </label>
              <input
                id="newsId"
                type="text"
                value={newsId}
                onChange={(e) => setNewsId(e.target.value)}
                placeholder="e.g., 02100311.20251205131222001"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <button
              type="submit"
              disabled={!newsId.trim()}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
            >
              <Search className="w-5 h-5" />
              Find & Edit Article
            </button>
          </form>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">How to find News ID:</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Visit <a href="https://en.sedaily.ai" target="_blank" className="underline">en.sedaily.ai</a></li>
              <li>Click on any article</li>
              <li>Copy the ID from the URL (after ?id=)</li>
              <li>Paste it here to edit</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
