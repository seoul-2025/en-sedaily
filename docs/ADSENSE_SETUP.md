# Google AdSense Setup Guide

This guide explains how to set up Google AdSense on the Seoul Economic Daily English website.

## Prerequisites

- A Google account
- Your website must be live and accessible (en.sedaily.com)
- The website must have sufficient content (at least 10-15 articles)
- The website must comply with [Google AdSense Program Policies](https://support.google.com/adsense/answer/48182)

---

## Step 1: Sign Up for Google AdSense

1. Go to https://www.google.com/adsense
2. Click **Get Started**
3. Sign in with your Google account
4. Fill out the application form:
   - **Website URL**: `en.sedaily.com`
   - **Content language**: English
   - **Country**: South Korea
5. Accept the AdSense Terms and Conditions
6. Submit your application

---

## Step 2: Add AdSense Code to Your Website

### 2.1 Get Your Publisher ID

1. After signing up, you'll receive a **Publisher ID** (looks like: `ca-pub-1234567890123456`)
2. Copy this ID - you'll need it for the next steps

### 2.2 Update Environment Variables

1. Open `frontend/.env.local`
2. Find the line: `NEXT_PUBLIC_ADSENSE_CLIENT_ID=`
3. Add your Publisher ID:
   ```
   NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-1234567890123456
   ```

### 2.3 Update ads.txt File

1. Open `frontend/public/ads.txt`
2. Replace `pub-XXXXXXXXXX` with your Publisher ID (without the `ca-` prefix):
   ```
   google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0
   ```

---

## Step 3: Create Ad Units in AdSense

Once your site is approved (usually takes 1-2 weeks), create ad units:

### 3.1 Create Display Ads

1. Log in to your AdSense account
2. Go to **Ads** → **By ad unit** → **Display ads**
3. Create the following ad units:

| Ad Unit Name | Type | Size | Used On |
|--------------|------|------|---------|
| Article Top Banner | Display ad | Responsive | Article pages (top) |
| Article Middle | Display ad | Responsive | Article pages (middle) |
| Article Bottom Banner | Display ad | Responsive | Article pages (bottom) |
| Homepage Top Banner | Display ad | Responsive | Homepage (top) |
| Homepage Bottom Banner | Display ad | Responsive | Homepage (bottom) |
| Category Sidebar 1 | Display ad | Rectangle (300x250) | Category pages (sidebar) |
| Category Sidebar 2 | Display ad | Rectangle (300x250) | Category pages (sidebar) |

### 3.2 Get Ad Slot IDs

After creating each ad unit, you'll receive an **Ad Slot ID** (looks like: `1234567890`)

---

## Step 4: Update Ad Slot IDs in Code

Replace the placeholder ad slot IDs with your actual IDs:

### Article Pages
File: `frontend/src/app/[category]/[year]/[month]/[day]/[slug]/page.tsx`

```typescript
{/* Ad 1: Top of Article */}
<AdLeaderboard adSlot="YOUR_ARTICLE_TOP_SLOT_ID" className="my-8" />

{/* Ad 2: Middle of Article */}
<AdInArticle adSlot="YOUR_ARTICLE_MIDDLE_SLOT_ID" />

{/* Ad 3: Bottom of Article */}
<AdLeaderboard adSlot="YOUR_ARTICLE_BOTTOM_SLOT_ID" className="my-8" />
```

### Homepage
File: `frontend/src/app/page.tsx`

```typescript
{/* Ad: Top of Homepage */}
<AdLeaderboard adSlot="YOUR_HOMEPAGE_TOP_SLOT_ID" className="mb-8" />

{/* Ad: Bottom of Homepage */}
<AdLeaderboard adSlot="YOUR_HOMEPAGE_BOTTOM_SLOT_ID" className="mt-12" />
```

### Category Pages
File: `frontend/src/app/[category]/CategoryClient.tsx`

```typescript
{/* Sidebar Ad 1 */}
<AdSidebar adSlot="YOUR_CATEGORY_SIDEBAR_1_SLOT_ID" />

{/* Sidebar Ad 2 */}
<AdSidebar adSlot="YOUR_CATEGORY_SIDEBAR_2_SLOT_ID" />
```

---

## Step 5: Deploy and Verify

### 5.1 Build and Deploy

```bash
cd frontend
npm run build
```

Deploy the built files to your production server.

### 5.2 Verify ads.txt

1. Visit https://en.sedaily.com/ads.txt
2. Verify it shows your Publisher ID
3. In AdSense dashboard, go to **Settings** → **Account** → **ads.txt**
4. Check that it says "Authorized"

### 5.3 Test Ads

1. Visit your website: https://en.sedaily.com
2. Open browser DevTools (F12) → Console
3. Look for AdSense script loading (no errors)
4. After 10-30 minutes, ads should start appearing

**Note**: During testing, you'll see placeholder boxes with "Ad Placeholder" text until you set the Client ID and deploy.

---

## Ad Placement Overview

### Homepage
```
┌─────────────────────────────┐
│ Header                      │
├─────────────────────────────┤
│ 📢 Top Banner (728x90)      │  ← Ad
├─────────────────────────────┤
│ Hero Section                │
│ Article Grid                │
│ Newsletter                  │
├─────────────────────────────┤
│ 📢 Bottom Banner (728x90)   │  ← Ad
└─────────────────────────────┘
```

### Article Page
```
┌─────────────────────────────┐
│ Article Title               │
├─────────────────────────────┤
│ 📢 Top Banner (728x90)      │  ← Ad
├─────────────────────────────┤
│ Article Image               │
│ Article Content (Part 1)    │
├─────────────────────────────┤
│ 📢 Middle Ad (300x250)      │  ← Ad
├─────────────────────────────┤
│ Article Content (Part 2)    │
│ Video Player (if exists)    │
├─────────────────────────────┤
│ 📢 Bottom Banner (728x90)   │  ← Ad
├─────────────────────────────┤
│ Related Articles            │
└─────────────────────────────┘
```

### Category Page
```
┌──────────────────┬──────────┐
│ Main Content     │ Sidebar  │
│                  │          │
│ Hero Article     │ 📢 Ad 1  │  ← Ad (300x250)
│                  │          │
│ Article List     │ Most Read│
│                  │          │
│                  │ 📢 Ad 2  │  ← Ad (300x250)
└──────────────────┴──────────┘
```

---

## Troubleshooting

### Ads Not Showing

1. **Check Environment Variable**
   - Verify `NEXT_PUBLIC_ADSENSE_CLIENT_ID` is set in `.env.local`
   - Restart dev server after changing env variables

2. **Check AdSense Account Status**
   - Make sure your account is approved
   - Check for policy violations in AdSense dashboard

3. **Check Browser Console**
   - Open DevTools → Console
   - Look for AdSense-related errors

4. **Check ads.txt**
   - Verify https://en.sedaily.com/ads.txt is accessible
   - Verify the Publisher ID matches your AdSense account

5. **Wait for Ad Serving**
   - New sites may take 24-48 hours for ads to start showing
   - AdSense needs to crawl and approve your pages

### Low CPM / Revenue

1. **Optimize Ad Placement**
   - Ads above the fold perform better
   - In-content ads have higher engagement

2. **Improve Content Quality**
   - High-quality, original content attracts better advertisers
   - Financial/business content typically has higher CPM

3. **Increase Traffic**
   - More pageviews = more ad impressions
   - Focus on SEO and content marketing

4. **Enable Auto Ads** (Optional)
   - In AdSense dashboard: **Ads** → **Auto ads**
   - Let Google automatically place ads

---

## Expected Revenue

For a news website with English financial content:

| Metric | Value |
|--------|-------|
| CPM (Cost per 1000 impressions) | $5-$15 |
| CTR (Click-through rate) | 1-3% |
| Monthly visitors (100,000) | ~$500-$1,500/month |

**Finance/Business content typically has 2-3x higher CPM than general content.**

---

## AdSense Policies to Follow

✅ **Do:**
- Publish original, high-quality content
- Make sure articles are well-written and informative
- Ensure proper attribution for quotes and data
- Keep ads clearly distinguishable from content

❌ **Don't:**
- Click your own ads (instant ban)
- Ask users to click ads ("Please support us by clicking ads")
- Place ads on error pages or empty pages
- Copy content from other sources without permission
- Place excessive ads (max 3 ads per page recommended)

---

## Additional Resources

- [AdSense Help Center](https://support.google.com/adsense)
- [AdSense Program Policies](https://support.google.com/adsense/answer/48182)
- [AdSense Optimization Tips](https://support.google.com/adsense/answer/17957)
- [ads.txt Guide](https://support.google.com/adsense/answer/7532444)

---

## Support

If you encounter issues:
1. Check the [AdSense Help Center](https://support.google.com/adsense)
2. Review browser console for errors
3. Contact AdSense support through your dashboard

---

**Last Updated**: December 30, 2024
