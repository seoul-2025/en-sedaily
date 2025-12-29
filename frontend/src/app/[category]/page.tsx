import { Metadata } from "next";
import { CategoryClient } from "./CategoryClient";
import { fetchCategoryArticles } from "@/utils/api";

const VALID_CATEGORIES = [
  "markets",
  "property",
  "finance",
  "business",
  "technology",
  "politics",
  "society",
  "culture",
  "sports",
  "international",
];

const CATEGORY_CONFIG: Record<
  string,
  { title: string; description: string; color: string }
> = {
  markets: {
    title: "South Korea Stock Markets & Securities",
    description: "Coverage of KOSPI, KOSDAQ, and Korean securities markets, including stock analysis and market trends.",
    color: "from-emerald-500 to-emerald-600",
  },
  property: {
    title: "South Korea Real Estate & Property",
    description: "Korean real estate market news, property trends, housing policy, and construction industry updates.",
    color: "from-amber-500 to-amber-600",
  },
  finance: {
    title: "South Korea Finance & Banking",
    description: "Financial news from South Korea, covering banking, investments, fintech, and monetary policy.",
    color: "from-green-500 to-green-600",
  },
  business: {
    title: "South Korea Business & Industry",
    description: "Korean business news covering major corporations, industrial sectors, semiconductors, and trade.",
    color: "from-slate-500 to-slate-600",
  },
  technology: {
    title: "South Korea Technology & Innovation News",
    description: "Coverage of South Korea's technology sector, including AI, semiconductors, startups, and digital innovation.",
    color: "from-indigo-500 to-indigo-600",
  },
  politics: {
    title: "South Korea Politics & Government Policy",
    description: "Latest news and analysis on South Korea's politics, government policies, diplomacy, and regulatory changes.",
    color: "from-blue-500 to-blue-600",
  },
  society: {
    title: "South Korea Society & Public Affairs",
    description: "In-depth coverage of South Korean society, including demographics, labor, education, housing, and social issues.",
    color: "from-purple-500 to-purple-600",
  },
  culture: {
    title: "South Korea Culture & Creative Industries",
    description: "Coverage of South Korea's culture, content industry, and creative sectors, including film, music, and cultural policy.",
    color: "from-pink-500 to-pink-600",
  },
  sports: {
    title: "South Korea Sports & Global Competitions",
    description: "News and analysis on South Korean sports, athletes, and the sports industry in international competitions.",
    color: "from-red-500 to-red-600",
  },
  international: {
    title: "Korea in Global Affairs",
    description: "International news and analysis related to South Korea's role in global politics, trade, and diplomacy.",
    color: "from-orange-500 to-orange-600",
  },
};

interface CategoryPageProps {
  params: { category: string };
}

// ISR: Revalidate every 60 seconds for fresh category content
export const revalidate = 60;

// Generate dynamic metadata for SEO & AI optimization
export async function generateMetadata({ params }: CategoryPageProps): Promise<Metadata> {
  const { category } = params;

  if (!VALID_CATEGORIES.includes(category)) {
    return {
      title: "Category Not Found - Seoul Economic Daily",
      description: "The requested category could not be found.",
    };
  }

  const config = CATEGORY_CONFIG[category];

  return {
    title: `${config.title} - Seoul Economic Daily`,
    description: config.description,
    keywords: `South Korea news, ${category}, Korean ${category}, Seoul Economic Daily, Korea business news`,
    alternates: {
      canonical: `https://en.sedaily.com/${category}`,
    },
    openGraph: {
      title: `${config.title} - Seoul Economic Daily`,
      description: config.description,
      url: `https://en.sedaily.com/${category}`,
      siteName: "Seoul Economic Daily",
      locale: "en_US",
      type: "website",
      images: [
        {
          url: "https://en.sedaily.com/sedaily-og-image.png",
          width: 1200,
          height: 630,
          alt: `${config.title} - Seoul Economic Daily`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: `${config.title} - Seoul Economic Daily`,
      description: config.description,
      site: "@sedaily_com",
      creator: "@sedaily_com",
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        "max-video-preview": -1,
        "max-image-preview": "large",
        "max-snippet": -1,
      },
    },
  };
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const { category } = params;

  if (!VALID_CATEGORIES.includes(category)) {
    return <div>Category not found</div>;
  }

  const config = CATEGORY_CONFIG[category];

  // Server-side data fetching for ISR
  let articles: any[] = [];
  let totalHits = 0;
  try {
    // 경제 카테고리는 키워드 필터링을 위해 더 많은 기사를 가져옴
    const pageSize = ['markets', 'property', 'finance', 'business'].includes(category) ? 100 : 20;
    const data = await fetchCategoryArticles(category, 1, pageSize);
    articles = data.articles || [];
    totalHits = data.total_hits || 0;
    
    // 경제 카테고리인 경우 서버에서 키워드 필터링
    const isEconomicCategory = ['markets', 'property', 'finance', 'business'].includes(category);
    if (isEconomicCategory) {
      const classifyArticle = (article: any) => {
        const title = article.title?.toLowerCase() || '';
        const content = article.content?.toLowerCase() || '';
        const text = title + ' ' + content;
        
        const marketsKeywords = ['증권', '증시', '주식', '주가', '코스피', 'kospi', '코스닥', 'kosdaq', '지수', '시가총액', '거래량', '상승', '하락', '급등', '급락', '변동성', '장', '공모주', 'ipo', '상장', '외국인', '기관', '개인 투자자', '투자', 'stock', 'stocks', 'equity', 'securities', 'market', 'index', 'share', 'trading', 'listing', '삼성전자', '현대차', 'sk하이닉스', 'lg', '포스코', '네이버', '카카오', '셀트리온', '매수', '매도', '시장', '투자자', '종목', '기업', '회사'];
        const propertyKeywords = ['부동산', '주택', '아파트', '주거', '분양', '미분양', '청약', '재건축', '재개발', '도시정비', '전세', '월세', '임대', '집값', '가격', '상업용', '오피스', '빌딩', '토지', '택지', 'pf', '건설', '건설사', '시공', '규제', '정책', 'real estate', 'property', 'housing', 'apartment', 'construction', '대림', '에스에이', '대우건설', '현대건설', '삼성물산'];
        const financeKeywords = ['금융', '금융권', '금융시장', '은행', '시중은행', '지방은행', '대출', '예금', '금리', '기준금리', '이자', '이자율', '통화', '통화정책', '외환', '환율', '달러', '원화', '외환시장', '무역', '수출', '수입', '무역수지', '경상수지', '국제수지', '금융정책', '재정정책', '보험', '보험사', '카드사', '결제', '자산운용', '펀드', '핀테크', 'finance', 'financial', 'bank', 'banking', 'interest rate', 'loan', 'credit', 'deposit', 'currency', 'exchange rate', 'foreign exchange', 'trade', 'exports', 'imports', 'monetary policy', 'financial policy'];
        const businessKeywords = ['산업', '기업', '기업들', '대기업', '중소기업', '스타트업', '경영', '경영 전략', '실적', '매출', '영업이익', '순이익', '투자', '설비 투자', '인수', '합병', 'm&a', '신사업', '사업 확장', '공장', '생산', '제조', '반도체', '디스플레이', '배터리', '유통', '소비', '리테일', '플랫폼', 'it 기업', '공급망', '밸류체인', '규제', '정책 영향', 'business', 'company', 'companies', 'corporate', 'management', 'earnings', 'revenue', 'profit', 'investment', 'capex', 'merger', 'acquisition', 'm&a', 'industry', 'manufacturing', 'semiconductor', 'retail', 'platform', 'supply chain'];
        
        if (marketsKeywords.some(keyword => text.includes(keyword))) return 'markets';
        if (propertyKeywords.some(keyword => text.includes(keyword))) return 'property';
        if (businessKeywords.some(keyword => text.includes(keyword))) return 'business';
        return 'finance';
      };
      
      articles = articles.filter(article => classifyArticle(article) === category);
    }
  } catch (error) {
    console.error('Error fetching category articles:', error);
  }

  // JSON-LD structured data for SEO & AI optimization
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: `${config.title} - Seoul Economic Daily`,
    description: config.description,
    url: `https://en.sedaily.com/${category}`,
    inLanguage: "en-US",
    isPartOf: {
      "@type": "WebSite",
      name: "Seoul Economic Daily",
      url: "https://en.sedaily.com",
    },
    publisher: {
      "@type": "NewsMediaOrganization",
      name: "Seoul Economic Daily",
      url: "https://en.sedaily.com",
      logo: {
        "@type": "ImageObject",
        url: "https://en.sedaily.com/sedaily-logo.png",
        width: 600,
        height: 60,
      },
    },
    mainEntity: {
      "@type": "ItemList",
      name: config.title,
      description: config.description,
      itemListElement: articles.slice(0, 10).map((article: any, index: number) => ({
        "@type": "ListItem",
        position: index + 1,
        item: {
          "@type": "NewsArticle",
          headline: article.title,
          url: `https://en.sedaily.com/${category}/${article.published_at.substring(0, 10).replace(/-/g, '/')}/${article.slug}`,
          datePublished: article.published_at,
        }
      })),
    },
  };



  // Regular category page for all categories
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="font-serif text-2xl font-bold tracking-wide text-[var(--color-primary)] mb-8">
            {config.title}
          </h1>
        </div>

        <CategoryClient
          category={category}
          config={config}
          initialArticles={articles}
          totalHits={totalHits}
        />
      </div>
    </>
  );
}
