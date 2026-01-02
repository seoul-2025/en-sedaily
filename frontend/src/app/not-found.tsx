import Link from 'next/link';
import { AlertCircle } from 'lucide-react';

export const metadata = {
  title: 'Page Not Found - Seoul Economic Daily',
  description: 'The page you are looking for could not be found.',
};

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto py-12 px-gutter">
      <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-6 rounded">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h1 className="text-2xl font-bold text-red-800 dark:text-red-200 mb-2">
              404 - Page Not Found
            </h1>
            <p className="text-red-700 dark:text-red-300 mb-4">
              The page you're looking for doesn't exist or has been moved.
            </p>
            <div className="flex gap-4">
              <Link 
                href="/" 
                className="text-[var(--color-accent)] hover:underline font-medium"
              >
                ← Back to Home
              </Link>
              <Link 
                href="/search" 
                className="text-[var(--color-accent)] hover:underline font-medium"
              >
                Search Articles
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <h2 className="font-semibold mb-3">Popular Categories</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['finance', 'technology', 'politics', 'society', 'culture', 'sports', 'international'].map((category) => (
            <Link
              key={category}
              href={`/${category}`}
              className="px-3 py-2 bg-white dark:bg-gray-700 rounded text-center capitalize hover:bg-accent hover:text-white transition-colors"
            >
              {category}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}