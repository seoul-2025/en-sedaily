'use client';

import { ShareButtons } from '../ShareButtons/ShareButtons';
import { FontSizeControl } from '../FontSizeControl/FontSizeControl';
import { PrintButton } from '../PrintButton/PrintButton';
import { AISummaryButton } from '../AISummary/AISummaryButton';

interface ArticleToolbarProps {
  title: string;
  url: string;
  description?: string;
  aiSummary?: string;
  aiKeyPoints?: string[];
  onSummaryToggle?: (isOpen: boolean) => void;
}

export function ArticleToolbar({ title, url, description, aiSummary, aiKeyPoints, onSummaryToggle }: ArticleToolbarProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-3 border-y border-[var(--color-border)] my-6 overflow-x-auto scrollbar-hide" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
      {/* Left: Share Buttons + Summary */}
      <div className="flex items-center gap-3 whitespace-nowrap">
        <ShareButtons title={title} url={url} description={description} />
        {aiSummary && aiKeyPoints && (
          <>
            <span className="text-gray-300 dark:text-gray-600">|</span>
            <AISummaryButton onToggle={onSummaryToggle} />
          </>
        )}
      </div>

      {/* Right: Font Size Control + Print */}
      <div className="flex items-center gap-2 whitespace-nowrap">
        <FontSizeControl />
        <PrintButton />
      </div>
    </div>
  );
}
