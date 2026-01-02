/**
 * Google Analytics 4 Event Tracking Utilities
 *
 * Usage:
 * import { trackEvent, trackArticleView, trackSearch } from '@/utils/analytics';
 *
 * trackArticleView({ title: '...', category: '...' });
 * trackSearch({ query: 'Samsung' });
 */

interface AnalyticsEvent {
  action: string;
  category: string;
  label?: string;
  value?: number;
}

/**
 * Track a custom event to GA4
 */
export function trackEvent({ action, category, label, value }: AnalyticsEvent) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    });

    if (process.env.NODE_ENV === 'development') {
      console.log('📊 GA4 Event:', { action, category, label, value });
    }
  }
}

/**
 * Track article view
 */
export function trackArticleView({
  title,
  category,
  newsId,
  author,
}: {
  title: string;
  category: string;
  newsId: string;
  author?: string;
}) {
  trackEvent({
    action: 'view_article',
    category: 'engagement',
    label: `${category} - ${title}`,
  });

  // Send as GA4 recommended event
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'view_item', {
      item_id: newsId,
      item_name: title,
      item_category: category,
      item_author: author,
    });
  }
}

/**
 * Track search query
 */
export function trackSearch({ query, resultsCount }: { query: string; resultsCount?: number }) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'search', {
      search_term: query,
      results_count: resultsCount,
    });
  }
}

/**
 * Track newsletter signup
 */
export function trackNewsletterSignup({ email }: { email: string }) {
  trackEvent({
    action: 'newsletter_signup',
    category: 'conversion',
    label: email,
  });

  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'sign_up', {
      method: 'newsletter',
    });
  }
}

/**
 * Track outbound link click
 */
export function trackOutboundLink({ url, label }: { url: string; label?: string }) {
  trackEvent({
    action: 'click_outbound',
    category: 'engagement',
    label: label || url,
  });

  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'click', {
      link_url: url,
      link_domain: new URL(url).hostname,
      outbound: true,
    });
  }
}

/**
 * Track social share
 */
export function trackSocialShare({ platform, url, title }: { platform: string; url: string; title: string }) {
  trackEvent({
    action: 'share',
    category: 'engagement',
    label: `${platform} - ${title}`,
  });

  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'share', {
      method: platform,
      content_type: 'article',
      item_id: url,
    });
  }
}

/**
 * Track category navigation
 */
export function trackCategoryView({ category }: { category: string }) {
  trackEvent({
    action: 'view_category',
    category: 'navigation',
    label: category,
  });
}

/**
 * Track video play
 */
export function trackVideoPlay({ videoId, title }: { videoId: string; title: string }) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'video_start', {
      video_title: title,
      video_provider: 'Naver TV',
      video_url: `https://tv.naver.com/v/${videoId}`,
    });
  }
}

/**
 * Track ad click
 */
export function trackAdClick({ adSlot, adPosition }: { adSlot: string; adPosition: string }) {
  trackEvent({
    action: 'ad_click',
    category: 'ads',
    label: `${adPosition} - ${adSlot}`,
  });
}

/**
 * Track 404 errors
 */
export function track404Error({ path }: { path: string }) {
  trackEvent({
    action: '404_error',
    category: 'error',
    label: path,
  });
}

/**
 * Track page timing (performance)
 */
export function trackPageTiming({
  name,
  value,
  category = 'performance',
}: {
  name: string;
  value: number;
  category?: string;
}) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'timing_complete', {
      name,
      value: Math.round(value),
      event_category: category,
    });
  }
}

/**
 * Track scroll depth
 */
export function trackScrollDepth({ depth }: { depth: number }) {
  trackEvent({
    action: 'scroll',
    category: 'engagement',
    label: `${depth}%`,
    value: depth,
  });
}
