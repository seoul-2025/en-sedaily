import Link from 'next/link';
import { Article } from '@/types/article';
import { formatDate } from '@/utils/formatDate';

interface SectionCardProps {
  title: string;
  articles: Article[];
}

function SectionCard({ title, articles }: SectionCardProps) {
  const [main, ...subs] = articles;

  return (
    <div className="border-b border-[var(--color-border)] pb-8">
      <h3 className="font-serif text-2xl font-bold mb-6 pb-3 border-b border-[var(--color-border)] text-[var(--color-primary)]">
        {title}
      </h3>

      {main && (
        <article className="mb-6 pb-6 border-b border-[var(--color-border)]">
          <Link href={main.url} className="block group">
            <h4 className="font-serif text-2xl font-bold leading-tight mb-3 text-[var(--color-text)] group-hover:text-[var(--color-accent)] transition-colors">
              {main.title}
            </h4>
            <time className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide">
              {formatDate(main.publishedAt)}
            </time>
          </Link>
        </article>
      )}

      {subs.length > 0 && (
        <div className="space-y-5">
          {subs.slice(0, 2).map((article) => (
            <article key={article.id} className="border-t border-[var(--color-border-light)] pt-5">
              <Link href={article.url} className="group block">
                <h5 className="font-serif text-base font-bold leading-snug mb-2 text-[var(--color-text)] group-hover:text-[var(--color-accent)] transition-colors">
                  {article.title}
                </h5>
                <time className="text-xs text-[var(--color-text-muted)] uppercase tracking-wide">
                  {formatDate(article.publishedAt)}
                </time>
              </Link>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

interface Props {
  sections: {
    title: string;
    articles: Article[];
  }[];
}

export function SectionGrid({ sections }: Props) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mb-12">
      {sections.map((section) => (
        <SectionCard key={section.title} {...section} />
      ))}
    </div>
  );
}
