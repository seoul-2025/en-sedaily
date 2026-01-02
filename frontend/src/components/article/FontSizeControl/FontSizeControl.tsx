'use client';

import { useState, useEffect } from 'react';

type FontSize = 'small' | 'medium' | 'large';

export function FontSizeControl() {
  const [fontSize, setFontSize] = useState<FontSize>('medium');

  // Load saved font size from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('article-font-size') as FontSize;
    if (saved && ['small', 'medium', 'large'].includes(saved)) {
      setFontSize(saved);
      applyFontSize(saved);
    }
  }, []);

  const applyFontSize = (size: FontSize) => {
    const article = document.querySelector('.article-content');
    if (!article) return;

    // Remove all size classes
    article.classList.remove('text-sm', 'text-base', 'text-lg');

    // Add appropriate class
    switch (size) {
      case 'small':
        article.classList.add('text-sm');
        break;
      case 'medium':
        article.classList.add('text-base');
        break;
      case 'large':
        article.classList.add('text-lg');
        break;
    }
  };

  const handleFontSizeChange = (size: FontSize) => {
    setFontSize(size);
    applyFontSize(size);
    localStorage.setItem('article-font-size', size);
  };

  return (
    <div className="flex items-center gap-1 border border-[var(--color-border)] rounded p-1">
      <button
        onClick={() => handleFontSizeChange('small')}
        className={`px-2 py-1 text-xs font-medium transition-colors ${
          fontSize === 'small'
            ? 'text-[var(--color-accent)]'
            : 'text-[var(--color-text-light)] hover:text-[var(--color-accent)]'
        }`}
        aria-label="Small font size"
        title="Small"
      >
        A
      </button>

      <button
        onClick={() => handleFontSizeChange('medium')}
        className={`px-2 py-1 text-sm font-medium transition-colors ${
          fontSize === 'medium'
            ? 'text-[var(--color-accent)]'
            : 'text-[var(--color-text-light)] hover:text-[var(--color-accent)]'
        }`}
        aria-label="Medium font size"
        title="Medium"
      >
        A
      </button>

      <button
        onClick={() => handleFontSizeChange('large')}
        className={`px-2 py-1 text-base font-medium transition-colors ${
          fontSize === 'large'
            ? 'text-[var(--color-accent)]'
            : 'text-[var(--color-text-light)] hover:text-[var(--color-accent)]'
        }`}
        aria-label="Large font size"
        title="Large"
      >
        A
      </button>
    </div>
  );
}
