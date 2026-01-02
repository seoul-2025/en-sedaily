'use client';

import { useEffect } from 'react';
import { trackArticleView } from '@/utils/analytics';

interface ArticleViewTrackerProps {
  title: string;
  category: string;
  newsId: string;
  author?: string;
}

/**
 * Article View Tracker Component
 *
 * Automatically tracks article views in Google Analytics when the component mounts.
 *
 * Usage:
 * <ArticleViewTracker
 *   title={article.title}
 *   category={article.category}
 *   newsId={article.news_id}
 *   author={article.byline}
 * />
 */
export function ArticleViewTracker({ title, category, newsId, author }: ArticleViewTrackerProps) {
  useEffect(() => {
    // Track article view when component mounts
    trackArticleView({
      title,
      category,
      newsId,
      author,
    });
  }, [title, category, newsId, author]);

  // This component doesn't render anything
  return null;
}
