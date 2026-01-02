# CMS Consolidation - 2025-01-08

## Problem

Two separate CMS systems existed:

1. **Admin API** (`admin.tf`) - Full CRUD with 5 Lambda functions - NOT USED
2. **Simple CMS** (`cms_delete.tf` + handlers) - 2 Lambda functions - CURRENTLY USED

## Solution

Keep Simple CMS (currently working), remove unused Admin API.

## Changes Made

### 1. Disabled Admin API Infrastructure

- Renamed `admin.tf` → `admin.tf.unused`
- Prevents Terraform from managing unused resources
- Saves ~$10/month (5 Lambda functions)

### 2. Current Active CMS

**Frontend:** https://enadmin.sedaily.ai
**Endpoints:**

- `POST /api/update-article` - Update article (cms_update_handler.py)
- `POST /api/delete-article` - Delete article (cms_delete_handler.py)

**Lambda Functions:**

- `seodaily-eng-cms-update-dev` (512MB, 30s)
- `seodaily-eng-cms-delete-dev` (512MB, 30s)

**Package:** `lambda-admin.zip`

### 3. Infrastructure Files

- ✅ `cms.tf` - S3 + CloudFront for frontend
- ✅ `cms_delete.tf` - Delete Lambda + API Gateway
- ✅ `route53_cms.tf` - DNS record for enadmin.sedaily.ai
- ❌ `admin.tf.unused` - Disabled (not used)

## Benefits

- ✅ Single CMS system (no confusion)
- ✅ Simpler architecture
- ✅ Cost savings (~$10/month)
- ✅ Easier maintenance

## If Admin API Needed Later

1. Rename `admin.tf.unused` → `admin.tf`
2. Update frontend to use `/admin/articles/*` endpoints
3. Run `terraform apply`
