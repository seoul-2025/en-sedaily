'use client';

import { Gamepad2, Grid3x3, Type, Target } from 'lucide-react';
import Link from 'next/link';

const games = [
  {
    name: 'Wordle',
    description: 'Guess the 5-letter word with 6 chances.',
    icon: Grid3x3,
    href: null,
  },
  {
    name: 'K-Business Connections',
    description: 'Group 16 Korean companies into 4 categories.',
    icon: Target,
    href: '/games/connections',
  },
  {
    name: 'Crossword',
    description: 'Get clued in with wordplay, every day.',
    icon: Type,
    href: null,
  },
  {
    name: 'Spelling Bee',
    description: 'How many words can you make with 7 letters?',
    icon: Gamepad2,
    href: null,
  },
];

export function GamesSection() {
  const handleGameClick = (gameName: string) => {
    alert(`${gameName} - Coming Soon!\n\nThis game will be available shortly. Stay tuned!`);
  };

  return (
    <section className="py-8 my-8 border-t border-b border-[var(--color-border)]">
      <div className="mb-6">
        <h2 className="text-xl font-serif font-bold text-[var(--color-primary)] mb-2">
          Games
        </h2>
        <p className="text-sm text-[var(--color-text-muted)]">
          Daily puzzles and brain teasers
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {games.map((game) => {
          const Icon = game.icon;
          const content = (
            <>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 flex items-center justify-center rounded-lg bg-[var(--color-accent)]/10 group-hover:bg-[var(--color-accent)]/20 transition-colors">
                  <Icon className="w-4 h-4 text-[var(--color-accent)]" />
                </div>
                <h3 className="text-base font-semibold text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                  {game.name}
                </h3>
              </div>
              <p className="text-xs text-[var(--color-text-light)] leading-relaxed">
                {game.description}
              </p>
            </>
          );

          if (game.href) {
            return (
              <Link
                key={game.name}
                href={game.href}
                className="group block p-4 border border-[var(--color-border)] rounded-lg hover:border-[var(--color-accent)] hover:shadow-md transition-all duration-200 text-left"
              >
                {content}
              </Link>
            );
          }

          return (
            <button
              key={game.name}
              onClick={() => handleGameClick(game.name)}
              className="group block p-4 border border-[var(--color-border)] rounded-lg hover:border-[var(--color-accent)] hover:shadow-md transition-all duration-200 text-left cursor-pointer"
            >
              {content}
            </button>
          );
        })}
      </div>
    </section>
  );
}
