'use client';

import { Printer } from 'lucide-react';

export function PrintButton() {
  const handlePrint = () => {
    window.print();
  };

  return (
    <button
      onClick={handlePrint}
      className="p-2 border border-[var(--color-border)] rounded transition-colors text-[var(--color-text-light)] hover:text-[var(--color-accent)]"
      aria-label="Print article"
      title="Print"
    >
      <Printer className="w-4 h-4" />
    </button>
  );
}
