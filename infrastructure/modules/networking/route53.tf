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

# Outputs
output "route53_record_fqdn" {
  description = "FQDN of the Route53 record"
  value       = aws_route53_record.main.fqdn
}

output "route53_record_com_fqdn" {
  description = "FQDN of the Route53 record for .com domain"
  value       = aws_route53_record.main_com.fqdn
}