# Google Analytics 4 (GA4) Setup Guide

This guide explains how to set up Google Analytics 4 on the Seoul Economic Daily English website to track user behavior and site performance.

## What is GA4?

Google Analytics 4 is the latest version of Google Analytics that provides:
- **Automatic event tracking** (page views, scrolls, outbound clicks, etc.)
- **Enhanced user journey analysis**
- **Cross-platform tracking** (web + app)
- **AI-powered insights and predictions**
- **Privacy-focused tracking** (cookieless options)

---

## Step 1: Create a GA4 Property

### 1.1 Sign Up for Google Analytics

1. Go to https://analytics.google.com
2. Sign in with your Google account
3. Click **Admin** (bottom left gear icon)

### 1.2 Create GA4 Property

1. In the **Property** column, click **Create Property**
2. Fill in the details:
   - **Property name**: `Seoul Economic Daily - English`
   - **Reporting time zone**: `(GMT+09:00) Seoul`
   - **Currency**: `US Dollar (USD)` or `Korean Won (KRW)`
3. Click **Next**

### 1.3 Business Information

1. Select **Industry category**: `News and media publishers`
2. Select **Business size**: Choose appropriate size
3. Select **How you intend to use Google Analytics**:
   - ✅ Measure advertising ROI
   - ✅ Examine user behavior
   - ✅ Analyze content performance
4. Click **Create**

### 1.4 Accept Terms

1. Accept the Google Analytics Terms of Service
2. Accept Data Processing Terms

---

## Step 2: Set Up Data Stream

### 2.1 Create Web Data Stream

1. In the **Property** column, click **Data Streams**
2. Click **Add stream** → **Web**
3. Fill in the details:
   - **Website URL**: `https://en.sedaily.com`
   - **Stream name**: `Seoul Economic Daily English Website`
4. Click **Create stream**

### 2.2 Get Your Measurement ID

After creating the stream, you'll see:

```
Measurement ID
G-XXXXXXXXXX
```

**Copy this ID** - you'll need it in the next step.

---

## Step 3: Configure Your Website

### 3.1 Add Measurement ID to Environment Variables

1. Open `frontend/.env.local`
2. Find the line: `NEXT_PUBLIC_GA4_MEASUREMENT_ID=`
3. Add your Measurement ID:
   ```
   NEXT_PUBLIC_GA4_MEASUREMENT_ID=G-ABC1234567
   ```

### 3.2 Restart Development Server

If you're running locally:
```bash
# Stop the server (Ctrl+C)
# Start again
npm run dev
```

### 3.3 Verify Installation

1. Visit your website: http://localhost:3000 (local) or https://en.sedaily.com (production)
2. Open browser DevTools (F12) → **Console** tab
3. You should see: `GA4: No measurement ID found` disappear (if you're in production mode)
4. Open DevTools → **Network** tab
5. Filter by `google-analytics.com` or `gtag`
6. You should see requests being sent

---

## Step 4: Verify Data Collection

### 4.1 Real-Time Report

1. Go back to Google Analytics
2. Click **Reports** (left sidebar) → **Realtime**
3. Visit your website in another tab
4. Within 30 seconds, you should see:
   - Active users count increases
   - Your page view appears in the report

### 4.2 DebugView (Optional - for Development)

1. In GA4 Admin → **Data Streams** → Click your stream
2. Scroll to **Enhanced measurement**
3. Click **DebugView** (shows development events)

---

## Automatic Event Tracking

The implementation automatically tracks:

### 🎯 Core Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `page_view` | User views a page | Every page load |
| `scroll` | User scrolls 90% | When reaching 90% of page |
| `click` | Outbound link clicks | Clicking external links |
| `file_download` | File downloads | Clicking downloadable files |

### 📊 Custom Events (Already Implemented)

| Event | Description | Location |
|-------|-------------|----------|
| `view_item` | Article view | Article detail pages |
| `search` | Search query | Search page |
| `newsletter_signup` | Newsletter subscription | Newsletter form |
| `share` | Social share | Share buttons (if added) |
| `video_start` | Video playback start | Naver TV videos |

---

## Tracked Metrics Overview

### Articles (Automatic)
When a user views an article, we track:
- Article title
- Category (finance, technology, etc.)
- Author name
- Article ID

**Code location:** `frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx`

### Search (Automatic)
When a user searches, we track:
- Search query
- Number of results found

**Code location:** `frontend/src/app/search/page.tsx`

---

## Custom Event Implementation

If you want to add more custom events in the future:

### Example: Track Newsletter Signup

```typescript
import { trackNewsletterSignup } from '@/utils/analytics';

// In your Newsletter component
const handleSubmit = (email: string) => {
  // ... your existing code ...

  // Track the event
  trackNewsletterSignup({ email });
};
```

### Example: Track Social Share

```typescript
import { trackSocialShare } from '@/utils/analytics';

const handleShare = (platform: 'twitter' | 'facebook' | 'linkedin') => {
  const url = window.location.href;
  const title = document.title;

  trackSocialShare({ platform, url, title });

  // ... open share dialog ...
};
```

### Available Tracking Functions

All functions are in `frontend/src/utils/analytics.ts`:

```typescript
trackEvent({ action, category, label, value })
trackArticleView({ title, category, newsId, author })
trackSearch({ query, resultsCount })
trackNewsletterSignup({ email })
trackOutboundLink({ url, label })
trackSocialShare({ platform, url, title })
trackCategoryView({ category })
trackVideoPlay({ videoId, title })
trackAdClick({ adSlot, adPosition })
track404Error({ path })
trackPageTiming({ name, value, category })
trackScrollDepth({ depth })
```

---

## Viewing Reports in GA4

### 1. Realtime Report
**Admin → Reports → Realtime**
- See active users right now
- See what pages they're viewing
- See events as they happen

### 2. Pages and Screens
**Admin → Reports → Engagement → Pages and screens**
- Most viewed pages
- Average engagement time per page
- Scroll depth

### 3. Events
**Admin → Reports → Engagement → Events**
- All tracked events
- Event counts
- Top events

### 4. User Acquisition
**Admin → Reports → Acquisition → User acquisition**
- Where users are coming from (Google, social media, direct, etc.)
- Traffic sources

### 5. Demographics
**Admin → Reports → User → Demographics**
- User countries
- Cities
- Languages

### 6. Tech Details
**Admin → Reports → Tech → Tech details**
- Browsers used
- Operating systems
- Screen resolutions
- Devices (desktop, mobile, tablet)

---

## Setting Up Goals & Conversions

### Mark Events as Conversions

1. Go to **Admin → Events**
2. Find your custom event (e.g., `newsletter_signup`)
3. Toggle **Mark as conversion** ON
4. Now you can see conversion metrics in reports

### Recommended Conversions

- `newsletter_signup` - Newsletter subscriptions
- `view_item` - Article views (if you want to track engagement)
- `search` - Searches (measure engagement)
- `share` - Social shares

---

## Advanced: Custom Dimensions (Optional)

If you want more detailed reporting, add custom dimensions:

### Example: Track Article Category

1. Go to **Admin → Data Display → Custom definitions**
2. Click **Create custom dimension**
3. Fill in:
   - **Dimension name**: `article_category`
   - **Scope**: Event
   - **Event parameter**: `item_category`
4. Save

Now you can filter reports by article category!

---

## Troubleshooting

### No Data Showing Up

1. **Check Measurement ID**
   - Verify `NEXT_PUBLIC_GA4_MEASUREMENT_ID` in `.env.local`
   - Make sure it starts with `G-`
   - Restart dev server after changing

2. **Check Browser Console**
   - Open DevTools → Console
   - Look for GA4-related errors
   - Check Network tab for `gtag` requests

3. **Check Ad Blockers**
   - Many ad blockers block Google Analytics
   - Try in incognito mode or different browser

4. **Wait for Data Processing**
   - Real-time reports show immediately
   - Standard reports may take 24-48 hours

### Events Not Tracking

1. **Check Function Calls**
   - Make sure you're calling tracking functions correctly
   - Check console for `📊 GA4 Event:` logs (development mode)

2. **Check Browser Support**
   - Make sure JavaScript is enabled
   - Check if `window.gtag` exists in console

3. **Verify Event Parameters**
   - Go to **Admin → Events**
   - Check if events are being received

---

## Privacy & GDPR Compliance

### Current Implementation

- ✅ **No cookies required** for basic tracking
- ✅ **IP anonymization** enabled by default in GA4
- ✅ **No personal data collected** (unless user provides email in newsletter)

### Recommended: Add Cookie Consent

For GDPR compliance, consider adding a cookie consent banner:

1. Install a consent library (e.g., `react-cookie-consent`)
2. Only load GA4 after user consents
3. Provide opt-out option

Example:
```typescript
// Conditional GA4 loading
{userConsented && <GoogleAnalytics />}
```

---

## Performance Impact

### Script Loading

- GA4 scripts load **after page is interactive** (`strategy="afterInteractive"`)
- **~30KB** total script size (minified + gzipped)
- **No blocking** of initial page render

### Best Practices

✅ **Do:**
- Keep GA4 script at the end of body
- Use `afterInteractive` loading strategy
- Minimize custom event parameters

❌ **Don't:**
- Load GA4 synchronously (blocks rendering)
- Track every single click (creates noise)
- Send large data objects in events

---

## Analytics Checklist

Before going live:

- [ ] GA4 property created
- [ ] Measurement ID added to `.env.local`
- [ ] Real-time report shows data
- [ ] Article views tracked correctly
- [ ] Search events tracked correctly
- [ ] No console errors
- [ ] Ad blocker doesn't break site
- [ ] Privacy policy updated (mention Google Analytics)
- [ ] Cookie consent added (if required by law)

---

## Key Metrics to Monitor

### Daily

- **Active users** (today)
- **Page views** (today)
- **Top articles** (today)
- **Bounce rate** (should be <60%)

### Weekly

- **User retention** (7-day returning users)
- **Traffic sources** (Google, social, direct)
- **Top search queries** (what users are searching for)
- **Average engagement time** (should be >2 minutes for articles)

### Monthly

- **New vs. returning users**
- **User acquisition trends**
- **Content performance** (which categories/topics perform best)
- **Device breakdown** (mobile vs. desktop)

---

## Resources

- [GA4 Documentation](https://support.google.com/analytics/answer/10089681)
- [GA4 Event Reference](https://support.google.com/analytics/answer/9267735)
- [GA4 vs Universal Analytics](https://support.google.com/analytics/answer/11986666)
- [GA4 Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)

---

## Support

If you need help:
1. Check [GA4 Help Center](https://support.google.com/analytics)
2. Visit [GA4 Community Forum](https://support.google.com/analytics/community)
3. Contact Google Analytics support through your account

---

**Last Updated**: December 30, 2024
