# CMS Infrastructure - Separate from main frontend

# S3 bucket for CMS frontend
resource "aws_s3_bucket" "cms" {
  bucket = "${var.project_name}-cms-${var.environment}-${var.region}"

  tags = {
    Name        = "${var.project_name}-cms"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_website_configuration" "cms" {
  bucket = aws_s3_bucket.cms.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "404.html"
  }
}

resource "aws_s3_bucket_public_access_block" "cms" {
  bucket = aws_s3_bucket.cms.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 bucket policy for CMS CloudFront access
resource "aws_s3_bucket_policy" "cms" {
  bucket = aws_s3_bucket.cms.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.cms.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.cms.arn
          }
        }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.cms]
}

# CloudFront Origin Access Control for CMS
resource "aws_cloudfront_origin_access_control" "cms" {
  name                              = "${var.project_name}-cms-oac"
  description                       = "OAC for ${var.project_name} CMS"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution for CMS
resource "aws_cloudfront_distribution" "cms" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = ["enadmin.sedaily.ai"]

  origin {
    domain_name              = aws_s3_bucket.cms.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.cms.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.cms.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.cms.id}"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = "arn:aws:acm:us-east-1:887078546492:certificate/ae647d30-3b86-429b-84b8-57398d536046"  # Wildcard *.sedaily.ai certificate
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  tags = {
    Name        = "${var.project_name}-cms-cdn"
    Environment = var.environment
  }
}

# Outputs for CMS
output "cms_cloudfront_domain" {
  description = "CMS CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.cms.domain_name
}

output "cms_cloudfront_id" {
  description = "CMS CloudFront distribution ID"
  value       = aws_cloudfront_distribution.cms.id
}

output "cms_s3_bucket_name" {
  description = "CMS S3 bucket name"
  value       = aws_s3_bucket.cms.id
}
