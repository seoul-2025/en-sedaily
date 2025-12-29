# CMS Password Authentication

**Last Updated**: 2025-01-08 (Phase 19)
**Status**: ✅ Production Ready

## Overview
Simple password authentication for CMS admin panel using localStorage.

## Authentication Details

### Password
- **Password**: `sedaily2024!`
- **Storage**: localStorage (`cms_auth` key)
- **Type**: Simple password check (no backend validation)

### Pages Structure
1. **`/` (Home)** - News ID input page (auth required)
2. **`/login`** - Password login page
3. **`/edit`** - Article editor (auth required)

## Implementation

### Login Flow
```
User visits https://enadmin.sedaily.ai/
  ↓
Redirects to /login (if not authenticated)
  ↓
User enters password: sedaily2024!
  ↓
localStorage.setItem('cms_auth', 'true')
  ↓
Redirect to / (News ID input)
```

### Auth Check
```typescript
useEffect(() => {
  const isAuth = localStorage.getItem('cms_auth');
  if (isAuth !== 'true') {
    router.push('/login');
  } else {
    setIsChecking(false);
  }
}, [router]);
```

### Logout
```typescript
const handleLogout = () => {
  localStorage.removeItem('cms_auth');
  router.push('/login');
};
```

## Files

### 1. Login Page
**File**: `cms/src/app/login/page.tsx`
- Password input field
- Submit button
- Error message display
- Lock icon (lucide-react)

### 2. Home Page (News ID Input)
**File**: `cms/src/app/page.tsx`
- Auth check on mount
- Logout button (top right)
- News ID input form
- Redirects to /edit?id={newsId}

### 3. Edit Page
**File**: `cms/src/app/edit/page.tsx`
- Auth check on mount
- Logout button (top right)
- Article editor
- Save/Delete/Cancel buttons

## Security Notes

### Current Implementation
- ✅ Simple password protection
- ✅ localStorage-based session
- ✅ Client-side validation only
- ✅ Logout functionality

### Limitations
- ⚠️ Password stored in code (not encrypted)
- ⚠️ No backend validation
- ⚠️ No session expiration
- ⚠️ No rate limiting
- ⚠️ No password reset

### Future Improvements (Optional)
1. AWS Cognito integration
2. JWT tokens
3. Session expiration
4. Password hashing
5. Multi-user support
6. Role-based access control

## Usage

### For Admins
1. Visit https://enadmin.sedaily.ai/
2. Enter password: `sedaily2024!`
3. Enter News ID to edit article
4. Click Logout when done

### For Developers
```bash
# Build CMS
cd cms
npm run build

# Deploy to S3
aws s3 sync out/ s3://seodaily-eng-cms-dev-us-east-1/ --delete

# Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id EAEB9I2CA0NDK --paths "/*"
```

## Troubleshooting

### Issue: Can't login
- Check password: `sedaily2024!` (case-sensitive)
- Clear browser cache
- Check localStorage in DevTools

### Issue: Logged out automatically
- localStorage cleared by browser
- Private/Incognito mode
- Browser settings blocking localStorage

### Issue: Stuck on loading
- Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
- Clear CloudFront cache
- Check browser console for errors

## Cost
- **Additional Cost**: $0 (client-side only)
- **Total CMS Cost**: ~$1/month (Lambda functions only)
