# Route53 record for en.sedaily.ai pointing to CloudFront
resource "aws_route53_record" "main" {
  zone_id = var.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }

  depends_on = [aws_cloudfront_distribution.main]
}

# Route53 record for en.sedaily.com pointing to CloudFront
resource "aws_route53_record" "main_com" {
  zone_id = var.zone_id  # Assuming same hosted zone, adjust if different
  name    = var.domain_name_com
  type    = "CNAME"
  ttl     = 300
  records = [var.domain_name]

  depends_on = [aws_route53_record.main]
}

# Google Search Console verification TXT record
resource "aws_route53_record" "google_verification" {
  zone_id = var.zone_id
  name    = var.domain_name_com
  type    = "TXT"
  ttl     = 300
  records = ["google-site-verification=dsPAuo6MbEnC5xXvub2mBP5Yu08es6fvLeRq41xqRI4"]
}