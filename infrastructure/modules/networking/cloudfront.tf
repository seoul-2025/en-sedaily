# CloudFront distribution for main frontend
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Seoul Economic Daily - EC2 SSR"
  default_root_object = ""
  
  # Domain aliases
  aliases = [
    var.domain_name,     # en.sedaily.ai
    var.domain_name_com  # en.sedaily.com
  ]

  # Origin configuration - EC2 instance
  origin {
    domain_name = "origin-en.sedaily.ai"
    origin_id   = "EC2-${var.project_name}"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
      origin_read_timeout    = 30
      origin_keepalive_timeout = 5
    }
    
    connection_attempts = 3
    connection_timeout  = 10
  }

  # Default cache behavior
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "EC2-${var.project_name}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    # Next.js requires forwarding headers for SSR
    forwarded_values {
      query_string = true
      headers      = ["Host", "Origin", "Referer"]
      
      cookies {
        forward = "all"
      }
    }

    # TTL settings for dynamic content
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 31536000
  }

  # Cache behavior for static assets
  ordered_cache_behavior {
    path_pattern           = "/_next/static/*"
    target_origin_id       = "EC2-${var.project_name}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 31536000  # 1 year
    default_ttl = 31536000  # 1 year
    max_ttl     = 31536000  # 1 year
  }

  # Cache behavior for API routes
  ordered_cache_behavior {
    path_pattern           = "/api/*"
    target_origin_id       = "EC2-${var.project_name}"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    compress               = false

    forwarded_values {
      query_string = true
      headers      = ["*"]
      
      cookies {
        forward = "all"
      }
    }

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0
  }

  # Geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # SSL certificate
  viewer_certificate {
    acm_certificate_arn      = var.ssl_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # Custom error responses for SPA behavior
  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/"
    error_caching_min_ttl = 10
  }

  # Price class
  price_class = "PriceClass_All"

  # Logging configuration (optional)
  # logging_config {
  #   include_cookies = false
  #   bucket         = "${var.project_name}-cloudfront-logs.s3.amazonaws.com"
  #   prefix         = "cloudfront-logs/"
  # }

  tags = {
    Name = "${var.project_name}-main-distribution"
  }

  depends_on = [aws_instance.web_server]
}

# Outputs
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.main.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID"
  value       = aws_cloudfront_distribution.main.hosted_zone_id
}