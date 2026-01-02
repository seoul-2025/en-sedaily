import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy - Seoul Economic Daily",
  description:
    "Privacy Policy for Seoul Economic Daily English edition. Learn how we collect, use, and protect your personal information.",
  keywords:
    "privacy policy, Seoul Economic Daily, 서울경제신문 개인정보처리방침, data protection",
  alternates: {
    canonical: "https://en.sedaily.com/privacy",
  },
  openGraph: {
    title: "Privacy Policy - Seoul Economic Daily",
    description:
      "Privacy Policy for Seoul Economic Daily English edition. Learn how we protect your data.",
    url: "https://en.sedaily.com/privacy",
    siteName: "Seoul Economic Daily",
    locale: "en_US",
    type: "website",
  },
};

export default function PrivacyPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: "Privacy Policy - Seoul Economic Daily",
    description: "Privacy Policy for Seoul Economic Daily English edition",
    url: "https://en.sedaily.com/privacy",
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
            Privacy Policy
          </h1>
          <p className="text-[var(--color-text-light)]">
            Last updated: December 18, 2025
          </p>
        </header>

        <article className="prose prose-lg max-w-none space-y-8">
          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Introduction
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Seoul Economic Daily Co., Ltd. (&quot;we,&quot; &quot;us,&quot; or
              &quot;our&quot;) respects your privacy and is committed to
              protecting your personal information. This Privacy Policy explains
              how we collect, use, disclose, and safeguard your information when
              you visit our English website (en.sedaily.com).
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Data Controller
            </h2>
            <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
              <p className="text-[var(--color-text)] mb-2">
                <strong>Company:</strong> Seoul Economic Daily Co., Ltd.
                (서울경제신문)
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>Address:</strong> Twin Tree Tower B, 14-16F, 6 Yulgok-ro,
                Jongno-gu, Seoul 03142, South Korea
              </p>
              <p className="text-[var(--color-text)] mb-2">
                <strong>Privacy Contact:</strong> webmaster@sedaily.com
              </p>
              <p className="text-[var(--color-text)]">
                <strong>Phone:</strong> +82-2-724-8600
              </p>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Information We Collect
            </h2>

            <h3 className="font-semibold text-lg text-[var(--color-primary)] mb-3">
              Automatically Collected Information
            </h3>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              When you visit our website, we may automatically collect certain
              information, including:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)] mb-6">
              <li>IP address and approximate geographic location</li>
              <li>Browser type and version</li>
              <li>Operating system</li>
              <li>Referring website</li>
              <li>Pages viewed and time spent on each page</li>
              <li>Date and time of access</li>
            </ul>

            <h3 className="font-semibold text-lg text-[var(--color-primary)] mb-3">
              Cookies and Tracking Technologies
            </h3>
            <p className="text-[var(--color-text)] leading-relaxed">
              We use cookies and similar tracking technologies to enhance your
              browsing experience, analyze site traffic, and understand where our
              visitors come from. You can control cookie settings through your
              browser preferences.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              How We Use Your Information
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              We may use the information we collect for the following purposes:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>To provide and maintain our news service</li>
              <li>To improve and optimize our website</li>
              <li>To analyze usage patterns and trends</li>
              <li>To detect and prevent technical issues or fraud</li>
              <li>To comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Legal Basis for Processing (GDPR)
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              For users in the European Economic Area (EEA), we process personal
              data based on the following legal grounds:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                <strong>Legitimate interests:</strong> To provide and improve our
                news services
              </li>
              <li>
                <strong>Consent:</strong> Where you have given consent for
                specific purposes
              </li>
              <li>
                <strong>Legal compliance:</strong> To comply with applicable laws
                and regulations
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Data Sharing and Disclosure
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              We may share your information in the following circumstances:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                <strong>Service providers:</strong> With third-party vendors who
                assist in operating our website (e.g., hosting, analytics)
              </li>
              <li>
                <strong>Legal requirements:</strong> When required by law or to
                respond to legal processes
              </li>
              <li>
                <strong>Business transfers:</strong> In connection with a merger,
                acquisition, or sale of assets
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Data Retention
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              We retain your personal information only for as long as necessary
              to fulfill the purposes outlined in this Privacy Policy, unless a
              longer retention period is required or permitted by law. Log data
              and analytics information are typically retained for 12 months.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Your Rights
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              Depending on your location, you may have the following rights
              regarding your personal information:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-[var(--color-text)]">
              <li>
                <strong>Access:</strong> Request a copy of your personal data
              </li>
              <li>
                <strong>Correction:</strong> Request correction of inaccurate
                data
              </li>
              <li>
                <strong>Deletion:</strong> Request deletion of your personal data
              </li>
              <li>
                <strong>Objection:</strong> Object to processing of your personal
                data
              </li>
              <li>
                <strong>Portability:</strong> Request transfer of your data to
                another service
              </li>
              <li>
                <strong>Withdrawal of consent:</strong> Withdraw previously given
                consent
              </li>
            </ul>
            <p className="text-[var(--color-text)] leading-relaxed mt-4">
              To exercise these rights, please contact us at
              webmaster@sedaily.com.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Korean Privacy Law (PIPA)
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Seoul Economic Daily complies with the Personal Information
              Protection Act (PIPA) of the Republic of Korea. Korean residents
              have additional rights under PIPA, including the right to request
              access to and correction of their personal information. For
              inquiries related to Korean privacy law, please contact
              webmaster@sedaily.com.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              International Data Transfers
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Your information may be transferred to and processed in countries
              other than your country of residence. We ensure appropriate
              safeguards are in place to protect your information in accordance
              with applicable data protection laws.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Security Measures
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              We implement appropriate technical and organizational security
              measures to protect your personal information against unauthorized
              access, alteration, disclosure, or destruction. However, no method
              of transmission over the Internet is 100% secure, and we cannot
              guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Children&apos;s Privacy
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Our website is not directed to children under the age of 14. We do
              not knowingly collect personal information from children. If you
              believe we have collected information from a child, please contact
              us immediately.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Third-Party Links
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              Our website may contain links to third-party websites. We are not
              responsible for the privacy practices of these external sites. We
              encourage you to review the privacy policies of any third-party
              sites you visit.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Changes to This Policy
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed">
              We may update this Privacy Policy from time to time. Any changes
              will be posted on this page with an updated revision date. We
              encourage you to review this policy periodically for any changes.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-4">
              Contact Us
            </h2>
            <p className="text-[var(--color-text)] leading-relaxed mb-4">
              If you have any questions or concerns about this Privacy Policy or
              our data practices, please contact us:
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
