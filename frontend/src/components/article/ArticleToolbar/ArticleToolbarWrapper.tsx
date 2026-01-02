'use client';

import { useState } from 'react';
import { ArticleToolbar } from './ArticleToolbar';
import { AISummary } from '../AISummary/AISummary';

interface ArticleToolbarWrapperProps {
  title: string;
  url: string;
  description?: string;
  aiSummary?: string;
  aiKeyPoints?: string[];
}

export function ArticleToolbarWrapper({
  title,
  url,
  description,
  aiSummary,
  aiKeyPoints
}: ArticleToolbarWrapperProps) {
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);

  return (
    <>
      <ArticleToolbar
        title={title}
        url={url}
        description={description}
        aiSummary={aiSummary}
        aiKeyPoints={aiKeyPoints}
        onSummaryToggle={setIsSummaryOpen}
      />
      <AISummary
        summary={aiSummary}
        keyPoints={aiKeyPoints}
        isOpen={isSummaryOpen}
      />
    </>
  );
}
