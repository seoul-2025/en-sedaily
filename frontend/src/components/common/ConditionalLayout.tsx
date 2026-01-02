'use client';

import { usePathname } from 'next/navigation';
import { Header } from '@/components/common/Header/Header';
import { Footer } from '@/components/common/Footer/Footer';
import { PageTransition } from '@/components/PageTransition';

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  // 게임 페이지에서는 Header와 Footer 숨기기
  const isGamePage = pathname?.startsWith('/games/connections');

  if (isGamePage) {
    return <>{children}</>;
  }

  return (
    <>
      <Header />
      <PageTransition>
        <main id="main-content" role="main" className="max-w-container mx-auto px-gutter py-6">
          {children}
        </main>
      </PageTransition>
      <Footer />
    </>
  );
}
