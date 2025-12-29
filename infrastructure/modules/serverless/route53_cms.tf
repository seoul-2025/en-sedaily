# Route 53 record for CMS

data "aws_route53_zone" "main" {
  name = "sedaily.ai"
}

resource "aws_route53_record" "cms" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "enadmin.sedaily.ai"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.cms.domain_name
    zone_id                = aws_cloudfront_distribution.cms.hosted_zone_id
    evaluate_target_health = false
  }
}
