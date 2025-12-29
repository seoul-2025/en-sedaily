import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service - Seoul Economic Daily",
  description:
    "Terms of Service for Seoul Economic Daily English edition. Read our terms and conditions for using en.sedaily.com.",
  keywords:
    "terms of service, Seoul Economic Daily, 서울경제신문 이용약관, news terms",
  alternates: {
    canonical: "https://en.sedaily.com/terms",
  },
  openGraph: {
    title: "Terms of Service - Seoul Economic Daily",
    description:
      "Terms of Service for Seoul Economic Daily English edition.",
    url: "https://en.sedaily.com/terms",
    siteName: "Seoul Economic Daily",
    locale: "en_US",
    type: "website",
  },
};

export default function TermsPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: "Terms of Service - Seoul Economic Daily",
    description: "Terms of Service for Seoul Economic Daily English edition",
    url: "https://en.sedaily.com/terms",
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
            Terms of Service
          </h1>
          <p className="text-[var(--color-text-light)]">
            Last updated: December 18, 2025
          </p>
        </header>

        <article className="prose prose-lg max-w-none space-y-8">
          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              1. Acceptance of Terms
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              By accessing and using the Seoul Economic Daily English website
              (en.sedaily.com), you accept and agree to be bound by these Terms
              of Service. If you do not agree to these terms, please do not use
              our services.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              2. Service Provider
            </h2>
            <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
              <p className="text-[var(--color-text)] mb-2">
                <strong>Company Name:</strong> Seoul Economic Daily Co., Ltd.
                (서울경제신문)
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>CEO & Publisher:</strong> Son Dong-young (손동영)
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>Address:</strong> Twin Tree Tower B, 14-16F, 6 Yulgok-ro,
                Jongno-gu, Seoul 03142, South Korea
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>Phone:</strong> +82-2-724-8600
              </p>
              <p className="text-[var(--color-text)]">
                <strong>Registration:</strong> Newspaper Reg. No. Seoul Ga-00224
                (May 13, 1988)
              </p>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              3. Intellectual Property Rights
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              All content published on Seoul Economic Daily, including but not
              limited to articles, photographs, graphics, videos, and other
              materials, is protected by copyright and other intellectual
              property laws.
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                Content may not be reproduced, distributed, or transmitted
                without prior written permission.
              </li>
              <li>
                Personal, non-commercial use such as reading and sharing links
                is permitted.
              </li>
              <li>
                For licensing inquiries, please contact webmaster@sedaily.com.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              4. Use of Service
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              You agree to use our services only for lawful purposes and in
              accordance with these Terms. You agree not to:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                Use the service in any way that violates applicable laws or
                regulations.
              </li>
              <li>
                Attempt to gain unauthorized access to any part of the service.
              </li>
              <li>
                Use automated systems or software to extract data from the
                website without permission.
              </li>
              <li>
                Interfere with or disrupt the integrity or performance of the
                service.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              5. News Content Disclaimer
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              Seoul Economic Daily strives to provide accurate and timely
              information. However:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                News content is provided for general information purposes only.
              </li>
              <li>
                Financial news and market information should not be construed as
                investment advice.
              </li>
              <li>
                We do not guarantee the accuracy, completeness, or timeliness of
                any information.
              </li>
              <li>
                Readers should verify information independently before making
                decisions.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              6. External Links
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Our website may contain links to third-party websites. Seoul
              Economic Daily is not responsible for the content, privacy
              policies, or practices of any third-party sites. We encourage you
              to review the terms and privacy policies of any external sites you
              visit.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              7. Limitation of Liability
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              To the fullest extent permitted by law, Seoul Economic Daily shall
              not be liable for any indirect, incidental, special, consequential,
              or punitive damages arising from your use of our services,
              including but not limited to loss of profits, data, or other
              intangible losses.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              8. Modifications to Terms
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Seoul Economic Daily reserves the right to modify these Terms of
              Service at any time. Changes will be effective immediately upon
              posting on this page. Your continued use of the service after any
              changes constitutes acceptance of the new terms.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              9. Governing Law
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              These Terms shall be governed by and construed in accordance with
              the laws of the Republic of Korea. Any disputes arising from these
              terms shall be subject to the exclusive jurisdiction of the courts
              of Seoul, South Korea.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              10. Contact Information
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              For questions about these Terms of Service, please contact us:
            </p>
            <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
              <p className="text-[var(--color-text)] mb-2">
                <strong>Email:</strong>{" "}
                <a
                  href="mailto:webmaster@sedaily.com"
                  className="text-[var(--color-accent)] hover:underline"
                >
                  webmaster@sedaily.com
                </a>
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>Phone:</strong> +82-2-724-8600
              </p>
              <p className="text-[var(--color-text)]">
                <strong>Address:</strong> Twin Tree Tower B, 14-16F, 6 Yulgok-ro,
                Jongno-gu, Seoul 03142, South Korea
              </p>
            </div>
          </section>
        </article>
      </div>
    </>
  );
}
