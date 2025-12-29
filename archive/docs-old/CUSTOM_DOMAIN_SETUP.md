# Custom Domain Setup Guide

**Domain**: eng.sedaily.ai

## Prerequisites

- AWS Account with ACM and Route 53 access
- Domain `sedaily.ai` managed in Route 53 or external DNS provider

## Step 1: Request ACM Certificate (us-east-1)

CloudFront requires certificates in us-east-1 region.

```bash
aws acm request-certificate \
  --domain-name eng.sedaily.ai \
  --validation-method DNS \
  --region us-east-1
```

**Output**: Copy the Certificate ARN
```
arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/CERTIFICATE_ID
```

## Step 2: Validate Certificate

### Get Validation Records

```bash
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/CERT_ID \
  --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
```

### Add DNS Record

**If using Route 53:**

```bash
# Get hosted zone ID
aws route53 list-hosted-zones --query "HostedZones[?Name=='sedaily.ai.'].Id" --output text

# Add CNAME record for validation
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_VALIDATION_NAME.eng.sedaily.ai",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "_VALIDATION_VALUE"}]
      }
    }]
  }'
```

**If using external DNS provider:**
- Add CNAME record manually in your DNS provider's console

### Wait for Validation

```bash
aws acm wait certificate-validated \
  --certificate-arn arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/CERT_ID \
  --region us-east-1
```

## Step 3: Update Terraform Configuration

Edit `infrastructure/terraform.tfvars`:

```hcl
acm_certificate_arn = "arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/CERT_ID"
```

## Step 4: Deploy Infrastructure

```bash
cd infrastructure
terraform plan
terraform apply
```

This will:
- Add `eng.sedaily.ai` as CloudFront alias
- Configure SSL certificate
- Enable SNI (Server Name Indication)

## Step 5: Add DNS Record for Domain

### Get CloudFront Domain Name

```bash
terraform output cloudfront_domain
# Output: d39c7rf2w6v6qi.cloudfront.net
```

### Add CNAME Record

**If using Route 53:**

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "eng.sedaily.ai",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "d39c7rf2w6v6qi.cloudfront.net"}]
      }
    }]
  }'
```

**If using external DNS provider:**
- Add CNAME record: `eng.sedaily.ai` → `d39c7rf2w6v6qi.cloudfront.net`

## Step 6: Verify Setup

### Test DNS Resolution

```bash
dig eng.sedaily.ai
nslookup eng.sedaily.ai
```

### Test HTTPS

```bash
curl -I https://eng.sedaily.ai
```

### Browser Test

Visit: https://eng.sedaily.ai

## Troubleshooting

### Certificate Validation Stuck

- Check DNS record is correct
- Wait up to 30 minutes for DNS propagation
- Verify CNAME record with `dig _validation.eng.sedaily.ai`

### CloudFront Error

- Ensure certificate is in us-east-1
- Check certificate status is "Issued"
- Verify domain matches exactly (no wildcards)

### DNS Not Resolving

- Wait for DNS propagation (up to 48 hours)
- Check CNAME record points to CloudFront domain
- Verify no conflicting A records

### SSL Certificate Error

- Ensure ACM certificate includes `eng.sedaily.ai`
- Check certificate is validated
- Verify CloudFront is using correct certificate ARN

## Rollback

If issues occur, revert to CloudFront default domain:

```bash
cd infrastructure
git checkout main.tf terraform.tfvars
terraform apply
```

## Cost

- ACM Certificate: **Free**
- Route 53 Hosted Zone: $0.50/month
- Route 53 Queries: $0.40 per million queries
- CloudFront: No additional cost for custom domain

## Security

- TLS 1.2+ enforced
- SNI (Server Name Indication) enabled
- HTTPS redirect automatic
- Certificate auto-renewal by ACM

## Maintenance

- ACM automatically renews certificates
- No manual intervention needed
- Monitor certificate expiration in ACM console

## Next Steps

After domain is live:

1. Update frontend environment variables
2. Update API CORS settings
3. Update documentation with new URL
4. Set up monitoring for custom domain
5. Configure Google Search Console with new domain
