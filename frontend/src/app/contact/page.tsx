import { Metadata } from "next";
import { Mail, Phone, MapPin, Globe, Clock } from "lucide-react";

export const metadata: Metadata = {
  title: "Contact Us - Seoul Economic Daily",
  description:
    "Contact Seoul Economic Daily for inquiries, feedback, or press information. Reach our editorial team in Seoul, South Korea.",
  keywords:
    "contact Seoul Economic Daily, 서울경제신문 연락처, Korean news contact, press inquiries",
  alternates: {
    canonical: "https://en.sedaily.com/contact",
  },
  openGraph: {
    title: "Contact Us - Seoul Economic Daily",
    description:
      "Contact Seoul Economic Daily for inquiries, feedback, or press information.",
    url: "https://en.sedaily.com/contact",
    siteName: "Seoul Economic Daily",
    locale: "en_US",
    type: "website",
  },
};

export default function ContactPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ContactPage",
    name: "Contact Seoul Economic Daily",
    description: "Contact information for Seoul Economic Daily",
    url: "https://en.sedaily.com/contact",
    mainEntity: {
      "@type": "NewsMediaOrganization",
      name: "Seoul Economic Daily",
      telephone: "+82-2-724-8600",
      address: {
        "@type": "PostalAddress",
        streetAddress: "Twin Tree Tower B, 14-16F, 6 Yulgok-ro, Jongno-gu",
        addressLocality: "Seoul",
        addressCountry: "KR",
        postalCode: "03142",
      },
      contactPoint: {
        "@type": "ContactPoint",
        telephone: "+82-2-724-8600",
        contactType: "customer service",
        availableLanguage: ["Korean", "English"],
      },
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
            Contact Us
          </h1>
          <p className="text-xl text-[var(--color-text-light)]">
            Get in touch with Seoul Economic Daily
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* Contact Cards */}
          <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[var(--color-accent)]/20 rounded-full flex items-center justify-center">
                <Phone className="w-5 h-5 text-[var(--color-accent)]" />
              </div>
              <h2 className="font-semibold text-lg text-[var(--color-primary)]">
                Phone
              </h2>
            </div>
            <p className="text-[var(--color-text)] mb-2">+82-2-724-8600</p>
            <p className="text-sm text-[var(--color-text-light)]">
              Main switchboard (Korean/English)
            </p>
          </div>

          <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[var(--color-accent)]/20 rounded-full flex items-center justify-center">
                <Mail className="w-5 h-5 text-[var(--color-accent)]" />
              </div>
              <h2 className="font-semibold text-lg text-[var(--color-primary)]">
                Email
              </h2>
            </div>
            <p className="text-[var(--color-text)] mb-2">
              <a
                href="mailto:webmaster@sedaily.com"
                className="text-[var(--color-accent)] hover:underline"
              >
                webmaster@sedaily.com
              </a>
            </p>
            <p className="text-sm text-[var(--color-text-light)]">
              General inquiries
            </p>
          </div>

          <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[var(--color-accent)]/20 rounded-full flex items-center justify-center">
                <MapPin className="w-5 h-5 text-[var(--color-accent)]" />
              </div>
              <h2 className="font-semibold text-lg text-[var(--color-primary)]">
                Address
              </h2>
            </div>
            <p className="text-[var(--color-text)] mb-2">
              Twin Tree Tower B, 14-16F
              <br />
              6 Yulgok-ro, Jongno-gu
              <br />
              Seoul 03142, South Korea
            </p>
            <p className="text-sm text-[var(--color-text-light)]">
              서울특별시 종로구 율곡로 6 트윈트리타워 B동 14~16층
            </p>
          </div>

          <div className="bg-[var(--color-bg-subtle)] p-6 rounded-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[var(--color-accent)]/20 rounded-full flex items-center justify-center">
                <Clock className="w-5 h-5 text-[var(--color-accent)]" />
              </div>
              <h2 className="font-semibold text-lg text-[var(--color-primary)]">
                Business Hours
              </h2>
            </div>
            <p className="text-[var(--color-text)] mb-2">
              Monday - Friday
              <br />
              9:00 AM - 6:00 PM (KST)
            </p>
            <p className="text-sm text-[var(--color-text-light)]">
              Korea Standard Time (UTC+9)
            </p>
          </div>
        </div>

        {/* Department Contacts */}
        <section className="mb-12">
          <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-6">
            Department Contacts
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border)]">
                  <th className="text-left py-3 px-4 text-[var(--color-primary)] font-semibold">
                    Department
                  </th>
                  <th className="text-left py-3 px-4 text-[var(--color-primary)] font-semibold">
                    Contact
                  </th>
                </tr>
              </thead>
              <tbody className="text-[var(--color-text)]">
                <tr className="border-b border-[var(--color-border-light)]">
                  <td className="py-3 px-4">Editorial Department</td>
                  <td className="py-3 px-4">+82-2-724-8600</td>
                </tr>
                <tr className="border-b border-[var(--color-border-light)]">
                  <td className="py-3 px-4">Advertising</td>
                  <td className="py-3 px-4">+82-2-724-8600</td>
                </tr>
                <tr className="border-b border-[var(--color-border-light)]">
                  <td className="py-3 px-4">Subscription</td>
                  <td className="py-3 px-4">+82-2-724-8600</td>
                </tr>
                <tr className="border-b border-[var(--color-border-light)]">
                  <td className="py-3 px-4">Digital/Web Services</td>
                  <td className="py-3 px-4">webmaster@sedaily.com</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Online Presence */}
        <section className="mb-12">
          <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-6">
            Follow Us
          </h2>
          <div className="flex flex-wrap gap-4">
            <a
              href="https://www.sedaily.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-subtle)] rounded-lg hover:bg-[var(--color-accent)]/10 transition-colors"
            >
              <Globe className="w-5 h-5 text-[var(--color-accent)]" />
              <span className="text-[var(--color-text)]">Website (Korean)</span>
            </a>
            <a
              href="https://www.youtube.com/channel/UCIkA31O7aWbr2kcloN8uP6X/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-subtle)] rounded-lg hover:bg-[var(--color-accent)]/10 transition-colors"
            >
              <span className="text-[var(--color-text)]">YouTube</span>
            </a>
            <a
              href="https://www.facebook.com/seouleconomydaily"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-subtle)] rounded-lg hover:bg-[var(--color-accent)]/10 transition-colors"
            >
              <span className="text-[var(--color-text)]">Facebook</span>
            </a>
            <a
              href="https://twitter.com/sedaily_com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-subtle)] rounded-lg hover:bg-[var(--color-accent)]/10 transition-colors"
            >
              <span className="text-[var(--color-text)]">Twitter</span>
            </a>
            <a
              href="https://www.instagram.com/sedaily_economic/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-subtle)] rounded-lg hover:bg-[var(--color-accent)]/10 transition-colors"
            >
              <span className="text-[var(--color-text)]">Instagram</span>
            </a>
          </div>
        </section>

        {/* Map Placeholder */}
        <section>
          <h2 className="font-serif text-2xl font-bold text-[var(--color-primary)] mb-6">
            Location
          </h2>
          <div className="bg-[var(--color-bg-subtle)] rounded-lg p-8 text-center">
            <MapPin className="w-12 h-12 text-[var(--color-accent)] mx-auto mb-4" />
            <p className="text-[var(--color-text)] mb-2">
              Twin Tree Tower B, Jongno-gu, Seoul
            </p>
            <p className="text-sm text-[var(--color-text-light)] mb-4">
              Near Jonggak Station (Line 1) & Anguk Station (Line 3)
            </p>
            <a
              href="https://map.naver.com/p/search/%EC%84%9C%EC%9A%B8%EA%B2%BD%EC%A0%9C%EC%8B%A0%EB%AC%B8"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              View on Map
            </a>
          </div>
        </section>
      </div>
    </>
  );
}
