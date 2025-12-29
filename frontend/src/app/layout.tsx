import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/common/Header/Header";
import { Footer } from "@/components/common/Footer/Footer";
import { ScrollToTop } from "@/components/ScrollToTop";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://en.sedaily.com'),
  title: "Seoul Economic Daily - Korea Business News, Stock Market, Finance & Economy",
  description: "Seoul Economic Daily provides latest Korean business news, KOSPI/KOSDAQ stock market updates, economy, finance, real estate, and technology news. Korea's leading economic newspaper in English.",
  keywords: "Seoul Economic, Korea business news, KOSPI, KOSDAQ, Korean economy, Samsung news, Hyundai, LG, SK, Korea finance, Korean companies, stock market Korea, Seoul news, economic news, financial analysis",
  authors: [{ name: "Seoul Economic Daily" }],
  publisher: "Seoul Economic Daily",
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon-32x32.png', sizes: '32x32' },
      { url: '/favicon-16x16.png', sizes: '16x16' }
    ],
    apple: '/apple-touch-icon.png',
  },
  alternates: {
    canonical: process.env.NEXT_PUBLIC_SITE_URL || "https://en.sedaily.com",
    languages: {
      'ko': 'https://www.sedaily.com',
      'en': 'https://en.sedaily.com',
    },
  },
  openGraph: {
    type: "website",
    siteName: "Seoul Economic Daily",
    title: "Seoul Economic Daily - Korea Business News & Financial Analysis",
    description: "Korea's leading economic newspaper. Latest business news, stock market, economy, finance, and technology updates in English.",
    locale: "en_US",
    url: process.env.NEXT_PUBLIC_SITE_URL || "https://en.sedaily.com",
    images: [
      {
        url: "https://en.sedaily.com/sedaily-og-image.png",
        width: 1200,
        height: 630,
        alt: "Seoul Economic Daily",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    site: "@sedaily_com",
    creator: "@sedaily_com",
    title: "Seoul Economic Daily",
    description: "Korea's leading economic newspaper. Business news, stock market, finance in English.",
    images: ["/sedaily-og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: "3Z6f3E3o-lUnRMbFvAk3UyJk7A0chF_WALvuU5_yB5Q",
  },
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0d1117',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="google-site-verification" content="3Z6f3E3o-lUnRMbFvAk3UyJk7A0chF_WALvuU5_yB5Q" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="msapplication-TileColor" content="#ffffff" />
        <meta name="theme-color" content="#ffffff" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href={process.env.NEXT_PUBLIC_API_BASE_URL || "https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com"} />
        {/* RSS Feeds */}
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - All News" href="https://en.sedaily.com/rss.xml" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Finance" href="https://en.sedaily.com/rss/finance" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Technology" href="https://en.sedaily.com/rss/technology" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Politics" href="https://en.sedaily.com/rss/politics" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Society" href="https://en.sedaily.com/rss/society" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Culture" href="https://en.sedaily.com/rss/culture" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - Sports" href="https://en.sedaily.com/rss/sports" />
        <link rel="alternate" type="application/rss+xml" title="Seoul Economic Daily - International" href="https://en.sedaily.com/rss/international" />
        {/* Enhanced NewsMediaOrganization Schema (GEO/AEO: E-E-A-T signals) */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "NewsMediaOrganization",
              "name": "Seoul Economic Daily",
              "alternateName": ["서울경제신문", "Seoul Economic", "SEdaily"],
              "url": "https://en.sedaily.com",
              "logo": {
                "@type": "ImageObject",
                "url": "https://en.sedaily.com/sedaily-logo.png",
                "width": 600,
                "height": 60
              },
              "foundingDate": "1960-05-09",
              "description": "Korea's first economic newspaper, established in 1960. Providing comprehensive coverage of Korean business, finance, technology, and economic news.",
              "address": {
                "@type": "PostalAddress",
                "addressCountry": "KR",
                "addressLocality": "Seoul",
                "addressRegion": "Seoul"
              },
              "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "editorial",
                "email": "webmaster@sedaily.com",
                "availableLanguage": ["English", "Korean"]
              },
              "publishingPrinciples": "https://en.sedaily.com/about",
              "ethicsPolicy": "https://en.sedaily.com/about",
              "sameAs": [
                "https://www.sedaily.com",
                "https://www.youtube.com/channel/UCIkA31O7aWbr2kcloN8uP6X/",
                "https://www.facebook.com/seouleconomydaily",
                "https://twitter.com/sedaily_com",
                "https://www.instagram.com/sedaily_economic/"
              ]
            })
          }}
        />

        {/* WebSite Schema with SearchAction (GEO/AEO: Search feature discovery) */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": "Seoul Economic Daily",
              "alternateName": "Seoul Economic English",
              "url": "https://en.sedaily.com",
              "description": "Korea's leading economic newspaper providing business news, stock market updates, and financial analysis in English.",
              "publisher": {
                "@type": "NewsMediaOrganization",
                "name": "Seoul Economic Daily",
                "url": "https://en.sedaily.com"
              },
              "potentialAction": {
                "@type": "SearchAction",
                "target": {
                  "@type": "EntryPoint",
                  "urlTemplate": "https://en.sedaily.com/search?q={search_term_string}"
                },
                "query-input": "required name=search_term_string"
              },
              "inLanguage": "en-US"
            })
          }}
        />
      </head>
      <body>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <Header />
        <main id="main-content" role="main" className="max-w-container mx-auto px-gutter py-12">
          {children}
        </main>

        <ScrollToTop />
        <Footer />
      </body>
    </html>
  );
}
