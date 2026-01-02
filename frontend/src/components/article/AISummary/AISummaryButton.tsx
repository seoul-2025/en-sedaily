'use client';

import { useState } from 'react';
import { Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface AISummaryButtonProps {
  onToggle?: (isOpen: boolean) => void;
}

export function AISummaryButton({ onToggle }: AISummaryButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleClick = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    if (onToggle) {
      onToggle(newState);
    }
  };

  return (
    <button
      onClick={handleClick}
      className="flex items-center gap-1.5 text-[var(--color-text-light)] hover:text-[var(--color-accent)] transition-colors"
      aria-label="AI Summary"
      aria-expanded={isOpen}
    >
      <Sparkles className="w-4 h-4" />
      <span className="text-sm font-medium">Summary</span>
      {isOpen ? (
        <ChevronUp className="w-4 h-4" />
      ) : (
        <ChevronDown className="w-4 h-4" />
      )}
    </button>
  );
}
