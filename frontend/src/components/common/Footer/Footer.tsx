import { Youtube, Tv, Instagram, Facebook, BookOpen, Rss } from 'lucide-react';

// X (Twitter) 아이콘 - lucide에 없어서 커스텀
const XIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

// Naver 아이콘 - 커스텀
const NaverIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M16.273 12.845 7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z" />
  </svg>
);

export function Footer() {
  const socialLinks = [
    {
      Icon: Youtube,
      label: 'YouTube',
      href: 'https://www.youtube.com/@%EC%84%9C%EC%9A%B8%EA%B2%BD%EC%A0%9C%EC%8B%A0%EB%AC%B8'
    },
    {
      Icon: Tv,
      label: 'Naver TV',
      href: 'https://tv.naver.com/sed.thumb'
    },
    {
      Icon: Instagram,
      label: 'Instagram',
      href: 'https://www.instagram.com/economy_dragon_/'
    },
    {
      Icon: NaverIcon,
      label: 'Naver Blog',
      href: 'https://blog.naver.com/sedaily_1960'
    },
    {
      Icon: Facebook,
      label: 'Facebook',
      href: 'https://www.facebook.com/seouleconomydaily/'
    },
    {
      Icon: XIcon,
      label: 'X',
      href: 'https://x.com/sedaily_com'
    },
    {
      Icon: Rss,
      label: 'RSS Feed',
      href: '/rss.xml'
    },
  ];

  return (
    <footer className="border-t border-[var(--color-border)] mt-16 bg-[var(--color-bg-subtle)]" role="contentinfo">
      <div className="max-w-container mx-auto px-gutter py-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
          <div className="font-serif text-2xl font-bold text-[var(--color-primary)]">
            Seoul Economic Daily
          </div>

          <nav className="flex gap-8" aria-label="Footer navigation">
            {['About', 'Contact', 'Terms', 'Privacy'].map((item) => (
              <a
                key={item}
                href={`/${item.toLowerCase()}`}
                className="text-sm text-[var(--color-text-light)] hover:text-[var(--color-primary)] transition-colors"
              >
                {item}
              </a>
            ))}
          </nav>

          <div className="flex gap-3">
            {socialLinks.map(({ Icon, label, href }) => (
              <a
                key={label}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={label}
                title={label}
                className="w-10 h-10 border border-[var(--color-border)] rounded-lg flex items-center justify-center text-[var(--color-text-light)] hover:text-[var(--color-primary)] hover:border-[var(--color-primary)] transition-all"
              >
                <Icon className="w-5 h-5" />
              </a>
            ))}
          </div>
        </div>

        <div className="text-center pt-8 border-t border-[var(--color-border)]">
          <p className="text-sm text-[var(--color-text-muted)]">
            © 2025 Seoul Economic Daily. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
