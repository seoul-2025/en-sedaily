import { Metadata } from "next";

export const metadata: Metadata = {
  title: "About Us - Seoul Economic Daily",
  description:
    "Seoul Economic Daily, South Korea's first economic newspaper founded in 1960. Leading Korean business journalism for over 60 years with coverage of finance, markets, technology, and industry.",
  keywords:
    "Seoul Economic Daily, 서울경제신문, Korean news, business newspaper, financial journalism, Korea media, 1960",
  alternates: {
    canonical: "https://en.sedaily.com/about",
  },
  openGraph: {
    title: "About Us - Seoul Economic Daily",
    description:
      "South Korea's first economic newspaper founded in 1960. Leading Korean business journalism for over 60 years.",
    url: "https://en.sedaily.com/about",
    siteName: "Seoul Economic Daily",
    locale: "en_US",
    type: "website",
  },
};

export default function AboutPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "AboutPage",
    name: "About Seoul Economic Daily",
    description:
      "South Korea's first economic newspaper founded in 1960.",
    url: "https://en.sedaily.com/about",
    mainEntity: {
      "@type": "NewsMediaOrganization",
      name: "Seoul Economic Daily",
      alternateName: "서울경제신문",
      url: "https://en.sedaily.com",
      foundingDate: "1960",
      foundingLocation: {
        "@type": "Place",
        name: "Seoul, South Korea",
      },
      address: {
        "@type": "PostalAddress",
        streetAddress: "Twin Tree Tower B, 14-16F, 6 Yulgok-ro, Jongno-gu",
        addressLocality: "Seoul",
        addressCountry: "KR",
      },
      logo: {
        "@type": "ImageObject",
        url: "https://en.sedaily.com/sedaily-logo.png",
        width: 600,
        height: 60,
      },
      sameAs: [
        "https://www.sedaily.com",
        "https://www.youtube.com/channel/UCIkA31O7aWbr2kcloN8uP6X/",
        "https://www.facebook.com/seouleconomydaily",
        "https://twitter.com/sedaily_com",
        "https://www.instagram.com/sedaily_economic/",
      ],
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="max-w-4xl mx-auto py-12 px-4">
        <header className="mb-12">
          <h1 className="font-serif text-4xl font-bold text-[var(--color-primary)] mb-4">
            About Seoul Economic Daily
          </h1>
          <p className="text-xl text-[var(--color-text-light)]">
            South Korea&apos;s First Economic Newspaper Since 1960
          </p>
        </header>

        <article className="prose prose-lg max-w-none">
          {/* History Section */}
          <section className="mb-12">
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Our History
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              Founded in 1960, Seoul Economic Daily (서울경제신문) is South Korea&apos;s
              first economic newspaper. For over six decades, we have been at the
              forefront of business journalism, chronicling South Korea&apos;s remarkable
              transformation from a developing nation into a global economic powerhouse.
            </p>
            <p className="text-[var(--color-text)] leading-relaxed">
              As a pioneer in Korean financial journalism, Seoul Economic Daily has
              consistently provided comprehensive coverage of the economy, financial
              markets, corporate developments, and international business news that
              shapes South Korea&apos;s position in the global economy.
            </p>
          </section>

          {/* Vision Section */}
          <section className="mb-12">
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Our Vision
            </h2>
            <div className="space-y-6">
              <div className="border-l-4 border-[var(--color-accent)] pl-6">
                <h3 className="font-semibold text-lg text-[var(--color-primary)] mb-2">
                  LEADING THE WAY
                </h3>
                <p className="text-[var(--color-text-light)]">
                  Setting the standard for economic journalism, leading Korea&apos;s growth
                  and development through trusted reporting.
                </p>
              </div>
              <div className="border-l-4 border-[var(--color-accent)] pl-6">
                <h3 className="font-semibold text-lg text-[var(--color-primary)] mb-2">
                  LEADING THE INNOVATION
                </h3>
                <p className="text-[var(--color-text-light)]">
                  Driving media innovation through transformative approaches and
                  paradigm-shifting leadership in digital journalism.
                </p>
              </div>
              <div className="border-l-4 border-[var(--color-accent)] pl-6">
                <h3 className="font-semibold text-lg text-[var(--color-primary)] mb-2">
                  LEADING THE NEXT
                </h3>
                <p className="text-[var(--color-text-light)]">
                  Guiding Korea&apos;s economic future and contributing to the global
                  economic order through forward-looking coverage.
                </p>
              </div>
            </div>
          </section>

          {/* English Edition */}
          <section className="mb-12">
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              English Edition
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              The English edition of Seoul Economic Daily (en.sedaily.com) serves the
              international community seeking insight into South Korea&apos;s dynamic
              economy and business landscape. Our English platform delivers:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>Real-time coverage of Korean business and market news</li>
              <li>Analysis of KOSPI and KOSDAQ market movements</li>
              <li>Coverage of major Korean corporations including Samsung, Hyundai, SK, and LG</li>
              <li>Insights into South Korea&apos;s technology sector and innovation ecosystem</li>
              <li>Reports on government economic policies and regulatory developments</li>
            </ul>
          </section>

          {/* Coverage Areas */}
          <section className="mb-12">
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Coverage Areas
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { title: "Finance & Markets", desc: "Securities, banking, investments, monetary policy" },
                { title: "Technology", desc: "Semiconductors, AI, startups, digital innovation" },
                { title: "Real Estate", desc: "Property markets, construction, urban development" },
                { title: "Industry", desc: "Manufacturing, automotive, shipbuilding, energy" },
                { title: "Politics & Policy", desc: "Government policies, regulations, trade" },
                { title: "International", desc: "Global economy, foreign relations, trade" },
                { title: "Culture & Lifestyle", desc: "Arts, entertainment, sports, trends" },
                { title: "Society", desc: "Demographics, labor, education, social issues" },
              ].map((item) => (
                <div
                  key={item.title}
                  className="p-4 bg-[var(--color-bg-subtle)] rounded-lg"
                >
                  <h3 className="font-semibold text-[var(--color-primary)] mb-1">
                    {item.title}
                  </h3>
                  <p className="text-sm text-[var(--color-text-light)]">{item.desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Company Info */}
          <section className="mb-12">
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Company Information
            </h2>
            <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
              <dl className="space-y-3">
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Company Name
                  </dt>
                  <dd className="text-[var(--color-text)]">
                    Seoul Economic Daily Co., Ltd. (서울경제신문)
                  </dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Founded
                  </dt>
                  <dd className="text-[var(--color-text)]">1960</dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    CEO & Publisher
                  </dt>
                  <dd className="text-[var(--color-text)]">Son Dong-young (손동영)</dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Address
                  </dt>
                  <dd className="text-[var(--color-text)]">
                    Twin Tree Tower B, 14-16F, 6 Yulgok-ro, Jongno-gu, Seoul, Korea
                    <br />
                    <span className="text-[var(--color-text-light)] text-sm">
                      (서울특별시 종로구 율곡로 6 트윈트리타워 B동 14~16층)
                    </span>
                  </dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Phone
                  </dt>
                  <dd className="text-[var(--color-text)]">+82-2-724-8600</dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Registration
                  </dt>
                  <dd className="text-[var(--color-text)]">
                    Newspaper Reg. No. Seoul Ga-00224 (May 13, 1988)
                    <br />
                    Internet News Reg. No. Seoul A-04065 (April 26, 2016)
                  </dd>
                </div>
                <div className="flex flex-col sm:flex-row sm:gap-4">
                  <dt className="font-semibold text-[var(--color-primary)] sm:w-40">
                    Website
                  </dt>
                  <dd className="text-[var(--color-text)]">
                    <a
                      href="https://www.sedaily.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--color-accent)] hover:underline"
                    >
                      www.sedaily.com
                    </a>{" "}
                    (Korean)
                    <br />
                    <a
                      href="https://en.sedaily.com"
                      className="text-[var(--color-accent)] hover:underline"
                    >
                      en.sedaily.com
                    </a>{" "}
                    (English)
                  </dd>
                </div>
              </dl>
            </div>
          </section>
        </article>
      </div>
    </>
  );
}
