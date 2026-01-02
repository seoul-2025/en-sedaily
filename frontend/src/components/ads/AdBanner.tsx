'use client';

import { useEffect, useRef } from 'react';

interface AdBannerProps {
  /**
   * AdSense ad slot ID (data-ad-slot)
   * Get this from Google AdSense dashboard when creating ad units
   */
  adSlot: string;

  /**
   * Ad format type
   * - auto: Responsive ad that adapts to container
   * - horizontal: Wide banner (728x90, 970x90)
   * - rectangle: Square/rectangle (300x250, 336x280)
   * - vertical: Skyscraper (120x600, 160x600)
   */
  adFormat?: 'auto' | 'horizontal' | 'rectangle' | 'vertical';

  /**
   * Custom styles for the ad container
   */
  style?: React.CSSProperties;

  /**
   * Custom className for styling
   */
  className?: string;
}

/**
 * Google AdSense Banner Component
 *
 * Usage:
 * <AdBanner adSlot="1234567890" adFormat="horizontal" />
 *
 * Before using:
 * 1. Sign up for Google AdSense: https://www.google.com/adsense
 * 2. Add your site and get approved
 * 3. Create ad units in AdSense dashboard
 * 4. Set NEXT_PUBLIC_ADSENSE_CLIENT_ID in .env.local
 */
export function AdBanner({
  adSlot,
  adFormat = 'auto',
  style,
  className = ''
}: AdBannerProps) {
  const adRef = useRef<HTMLModElement>(null);

  useEffect(() => {
    // Push ad to AdSense queue
    try {
      if (typeof window !== 'undefined') {
        ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({});
      }
    } catch (error) {
      console.error('AdSense error:', error);
    }
  }, []);

  // Get client ID from environment variable
  const clientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID;

  // Don't render if no client ID is set
  if (!clientId) {
    return (
      <div className={`border border-dashed border-gray-300 p-4 text-center text-sm text-gray-500 ${className}`}>
        Ad Placeholder (Set NEXT_PUBLIC_ADSENSE_CLIENT_ID)
      </div>
    );
  }

  return (
    <div className={`ad-container ${className}`} style={style}>
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={{
          display: 'block',
          textAlign: 'center',
          minHeight: adFormat === 'rectangle' ? '250px' : '90px',
        }}
        data-ad-client={clientId}
        data-ad-slot={adSlot}
        data-ad-format={adFormat}
        data-full-width-responsive="true"
      />
    </div>
  );
}

/**
 * In-Article Ad Component (optimized for content)
 */
export function AdInArticle({ adSlot, className = '' }: { adSlot: string; className?: string }) {
  return (
    <AdBanner
      adSlot={adSlot}
      adFormat="auto"
      className={className}
      style={{
        margin: '2rem 0',
        padding: '1rem 0',
      }}
    />
  );
}

/**
 * Sidebar Ad Component (fixed rectangle)
 */
export function AdSidebar({ adSlot, className = '' }: { adSlot: string; className?: string }) {
  return (
    <div className={`sticky top-4 ${className}`}>
      <div className="text-xs text-gray-400 mb-2 text-center">Advertisement</div>
      <AdBanner
        adSlot={adSlot}
        adFormat="rectangle"
        style={{
          minHeight: '250px',
        }}
      />
    </div>
  );
}

/**
 * Leaderboard Ad Component (top/bottom banners)
 */
export function AdLeaderboard({ adSlot, className = '' }: { adSlot: string; className?: string }) {
  return (
    <div className={`w-full bg-gray-50 py-4 ${className}`}>
      <div className="text-xs text-gray-400 mb-2 text-center">Advertisement</div>
      <AdBanner
        adSlot={adSlot}
        adFormat="horizontal"
        style={{
          maxWidth: '970px',
          margin: '0 auto',
        }}
      />
    </div>
  );
}
