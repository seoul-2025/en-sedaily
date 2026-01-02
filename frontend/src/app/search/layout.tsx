import { Metadata } from "next";

/**
 * Search Page Layout with SEO Metadata
 *
 * SEO Strategy:
 * - robots: noindex, follow (검색 결과 페이지는 색인 제외, 링크는 팔로우)
 * - canonical: 기본 검색 페이지 URL로 설정
 *
 * Reference:
 * - Google SEO Guide: 검색 결과 페이지는 noindex 권장
 * - https://developers.google.com/search/docs/crawling-indexing/block-indexing
 */

export const metadata: Metadata = {
  title: "Search Articles - Seoul Economic Daily",
  description:
    "Search news articles from Seoul Economic Daily, South Korea's leading business and financial news source. Find coverage on Korean economy, markets, technology, and more.",
  keywords:
    "search Seoul Economic Daily, Korea news search, Korean business news, South Korea articles",
  alternates: {
    canonical: "https://en.sedaily.com/search",
  },
  openGraph: {
    title: "Search Articles - Seoul Economic Daily",
    description:
      "Search news articles from Seoul Economic Daily, South Korea's leading business and financial news source.",
    url: "https://en.sedaily.com/search",
    siteName: "Seoul Economic Daily",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Search Articles - Seoul Economic Daily",
    description:
      "Search news articles from Seoul Economic Daily, South Korea's leading business and financial news source.",
    site: "@sedaily_com",
  },
  robots: {
    index: false, // 검색 결과 페이지는 색인 제외
    follow: true, // 내부 링크는 팔로우
    googleBot: {
      index: false,
      follow: true,
    },
  },
};

export default function SearchLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
