'use client';

import Script from 'next/script';

interface GoogleAnalyticsProps {
  measurementId?: string;
}

/**
 * Google Analytics 4 (GA4) Component
 *
 * Automatically tracks:
 * - Page views
 * - Scroll depth
 * - Outbound clicks
 * - File downloads
 *
 * Usage:
 * Add to layout.tsx:
 * <GoogleAnalytics />
 *
 * Before using:
 * 1. Create GA4 property: https://analytics.google.com
 * 2. Get Measurement ID (format: G-XXXXXXXXXX)
 * 3. Set NEXT_PUBLIC_GA4_MEASUREMENT_ID in .env.local
 */
export function GoogleAnalytics({ measurementId }: GoogleAnalyticsProps) {
  const gaId = measurementId || process.env.NEXT_PUBLIC_GA4_MEASUREMENT_ID;

  // Don't render if no measurement ID is set
  if (!gaId) {
    if (process.env.NODE_ENV === 'development') {
      console.log('GA4: No measurement ID found. Set NEXT_PUBLIC_GA4_MEASUREMENT_ID to enable analytics.');
    }
    return null;
  }

  return (
    <>
      {/* Google Analytics Script */}
      <Script
        strategy="afterInteractive"
        src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
      />

      {/* GA4 Configuration */}
      <Script
        id="google-analytics"
        strategy="afterInteractive"
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', '${gaId}', {
              page_path: window.location.pathname,
              send_page_view: true,
              // Enhanced measurement (automatic tracking)
              enhanced_measurement: true,
              // Debug mode (only in development)
              debug_mode: ${process.env.NODE_ENV === 'development'}
            });
          `,
        }}
      />
    </>
  );
}

/**
 * Declare gtag function for TypeScript
 */
declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'set',
      targetId: string,
      config?: Record<string, any>
    ) => void;
    dataLayer: any[];
  }
}
