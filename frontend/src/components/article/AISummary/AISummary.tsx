'use client';

import { Sparkles } from 'lucide-react';

interface AISummaryProps {
  summary?: string;
  keyPoints?: string[];
  isOpen: boolean;
}

export function AISummary({ summary, keyPoints, isOpen }: AISummaryProps) {
  // AI Summary가 없으면 렌더링하지 않음
  if (!summary || !keyPoints || keyPoints.length === 0) {
    return null;
  }

  // 닫혀있으면 렌더링하지 않음
  if (!isOpen) {
    return null;
  }

  return (
    <div className="mb-8 overflow-hidden animate-slideDown">
      <div className="px-8 py-6 border border-gray-200 dark:border-gray-700">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-100 dark:border-gray-800">
          <Sparkles className="w-5 h-5 text-[var(--color-accent)]" />
          <div className="flex items-baseline gap-3">
            <h3 className="text-lg font-semibold text-[var(--color-primary)] tracking-tight">
              Article Summary
            </h3>
            <span className="text-xs text-[var(--color-text-muted)] font-medium">
              AI-powered • Editor reviewed
            </span>
          </div>
        </div>

        {/* Main Summary */}
        <div className="mb-6">
          <p className="text-base leading-[1.8] text-[var(--color-text)] font-normal">
            {summary}
          </p>
        </div>

        {/* Key Points */}
        {keyPoints && keyPoints.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-[var(--color-primary)] mb-4 uppercase tracking-wide">
              Key Topics
            </h4>
            <ul className="space-y-3">
              {keyPoints.map((point, index) => (
                <li key={index} className="flex items-start gap-3 group">
                  <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded bg-[var(--color-accent)] text-white text-xs font-bold mt-0.5">
                    {index + 1}
                  </span>
                  <span className="flex-1 text-[15px] text-[var(--color-text-light)] leading-[1.7]">
                    {point}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            max-height: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            max-height: 1000px;
            transform: translateY(0);
          }
        }

        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
