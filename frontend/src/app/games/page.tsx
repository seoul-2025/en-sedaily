import { Metadata } from "next";
import Link from "next/link";
import { Grid3x3, Type, Grid2X2, Sparkles } from "lucide-react";

export const metadata: Metadata = {
  title: "Games - Seoul Economic Daily",
  description: "Daily puzzles and brain teasers about Korean business and economy",
};

const games = [
  {
    id: "wordle",
    name: "Wordle",
    description: "Guess the 5-letter word with 6 chances.",
    icon: Grid2X2,
    available: false,
  },
  {
    id: "connections",
    name: "K-Business Connections",
    description: "Group 16 Korean companies into 4 categories.",
    icon: Grid3x3,
    available: true,
  },
  {
    id: "crossword",
    name: "Crossword",
    description: "Get clued in with wordplay, every day.",
    icon: Type,
    available: false,
  },
  {
    id: "spelling-bee",
    name: "Spelling Bee",
    description: "How many words can you make with 7 letters?",
    icon: Sparkles,
    available: false,
  },
];

export default function GamesPage() {
  return (
    <div className="max-w-6xl mx-auto py-12 px-gutter">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-[var(--color-primary)] mb-2">
          Games
        </h1>
        <p className="text-base text-[var(--color-text-light)]">
          Daily puzzles and brain teasers
        </p>
      </header>

      {/* Games Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {games.map((game) => {
          const Icon = game.icon;

          if (!game.available) {
            return (
              <div
                key={game.id}
                className="p-6 border border-[var(--color-border)] rounded-lg bg-white hover:shadow-md transition-shadow cursor-not-allowed opacity-60"
              >
                <div className="flex items-center gap-3 mb-3">
                  <Icon className="w-6 h-6 text-[var(--color-text-light)]" />
                  <h2 className="text-xl font-bold text-[var(--color-primary)]">
                    {game.name}
                  </h2>
                </div>

                <p className="text-sm text-[var(--color-text-light)] leading-relaxed">
                  {game.description}
                </p>
              </div>
            );
          }

          return (
            <Link
              key={game.id}
              href={`/games/${game.id}`}
              className="p-6 border border-[var(--color-border)] rounded-lg bg-white hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 mb-3">
                <Icon className="w-6 h-6 text-[var(--color-accent)]" />
                <h2 className="text-xl font-bold text-[var(--color-primary)]">
                  {game.name}
                </h2>
              </div>

              <p className="text-sm text-[var(--color-text-light)] leading-relaxed">
                {game.description}
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
