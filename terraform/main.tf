variable "prj_prefix" {}
variable "region_api" {}
variable "region_site" {}
variable "region_acm" {}
variable "route53_zone_id" {}
variable "domain_api" {}
variable "domain_static_site" {}
variable "domain_media_site" {}

provider "aws" {
  region = var.region_api
  alias  = "api"
}

provider "aws" {
  region = var.region_site
  alias  = "site"
}

provider "aws" {
  region = var.region_acm
  alias  = "acm"
}

terraform {
  backend "s3" {
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.74.2"
    }
  }
}

locals {
  fqdn = {
    api         = var.domain_api
    static_site = var.domain_static_site
    media_site  = var.domain_media_site
  }
  bucket = {
    static_site = local.fqdn.static_site
    media_site  = local.fqdn.media_site
  }
}

### S3 for cloudfront logs
#resource "aws_s3_bucket" "accesslog_static_site" {
#  provider      = aws.site
#  bucket        = "${local.fqdn.static_site}-accesslog"
#  force_destroy = true # Set true, destroy bucket with objects
#  acl           = "log-delivery-write"
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "s3", "accesslog_static_site"])
#    ManagedBy = "terraform"
#  }
#}


resource "aws_acm_certificate" "api" {
  provider          = aws.api
  domain_name       = local.fqdn.api
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}

resource "aws_acm_certificate" "static_site" {
  provider          = aws.acm
  domain_name       = local.fqdn.static_site
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm_static_site"])
    ManagedBy = "terraform"
  }
}

resource "aws_acm_certificate" "media_site" {
  provider          = aws.acm
  domain_name       = local.fqdn.media_site
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm_media_site"])
    ManagedBy = "terraform"
  }
}

# CNAME Record
resource "aws_route53_record" "api_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

resource "aws_route53_record" "static_site_acm_c" {
  for_each = {
    for d in aws_acm_certificate.static_site.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

resource "aws_route53_record" "media_site_acm_c" {
  for_each = {
    for d in aws_acm_certificate.media_site.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

## Related ACM Certification and CNAME record
resource "aws_acm_certificate_validation" "api" {
  provider                = aws.api
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.api_acm_c : record.fqdn]
}
resource "aws_acm_certificate_validation" "static_site" {
  provider                = aws.acm
  certificate_arn         = aws_acm_certificate.static_site.arn
  validation_record_fqdns = [for record in aws_route53_record.static_site_acm_c : record.fqdn]
}
resource "aws_acm_certificate_validation" "media_site" {
  provider                = aws.acm
  certificate_arn         = aws_acm_certificate.media_site.arn
  validation_record_fqdns = [for record in aws_route53_record.media_site_acm_c : record.fqdn]
}

## A record
resource "aws_route53_record" "static_site_cdn_a" {
  zone_id = var.route53_zone_id
  name    = local.fqdn.static_site
  type    = "A"
  alias {
    evaluate_target_health = true
    name                   = aws_cloudfront_distribution.static_site.domain_name
    zone_id                = aws_cloudfront_distribution.static_site.hosted_zone_id
  }
}
resource "aws_route53_record" "media_site_cdn_a" {
  zone_id = var.route53_zone_id
  name    = local.fqdn.media_site
  type    = "A"
  alias {
    evaluate_target_health = true
    name                   = aws_cloudfront_distribution.media_site.domain_name
    zone_id                = aws_cloudfront_distribution.media_site.hosted_zone_id
  }
}

# Create CloudFront OAI
resource "aws_cloudfront_origin_access_identity" "static_site" {
  comment = "Origin Access Identity for s3 ${local.bucket.static_site} bucket"
}
resource "aws_cloudfront_origin_access_identity" "media_site" {
  comment = "Origin Access Identity for s3 ${local.bucket.media_site} bucket"
}

## Cache Policy
data "aws_cloudfront_cache_policy" "managed_caching_optimized" {
  name = "Managed-CachingOptimized"
}
data "aws_cloudfront_cache_policy" "managed_caching_disabled" {
  name = "Managed-CachingDisabled"
}

## Distribution
resource "aws_cloudfront_distribution" "static_site" {
  origin {
    domain_name = "${local.bucket.static_site}.s3.${var.region_site}.amazonaws.com"
    origin_id   = "S3-${local.fqdn.static_site}"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.static_site.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Alternate Domain Names (CNAMEs)
  aliases = [local.fqdn.static_site]

  # Config for SSL Certification
  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = aws_acm_certificate.static_site.arn
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }

  retain_on_delete = false

  #logging_config {
  #  include_cookies = true
  #  bucket          = "${aws_s3_bucket.accesslog_static_site.id}.s3.amazonaws.com"
  #  prefix          = "log/static/prd/cf/"
  #}

  # For SPA to catch all request by /index.html
  custom_error_response {
    #error_caching_min_ttl = 360
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    #error_caching_min_ttl = 360
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${local.fqdn.static_site}"
    #viewer_protocol_policy = "allow-all"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    cache_policy_id        = data.aws_cloudfront_cache_policy.managed_caching_optimized.id
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

resource "aws_cloudfront_distribution" "media_site" {
  origin {
    domain_name = "${local.bucket.media_site}.s3.${var.region_site}.amazonaws.com"
    origin_id   = "S3-${local.fqdn.media_site}"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.media_site.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  # Alternate Domain Names (CNAMEs)
  aliases = [local.fqdn.media_site]

  # Config for SSL Certification
  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = aws_acm_certificate.media_site.arn
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }

  retain_on_delete = false

  #logging_config {
  #  include_cookies = true
  #  bucket          = "${aws_s3_bucket.accesslog_static_site.id}.s3.amazonaws.com"
  #  prefix          = "log/media/prd/cf/"
  #}

  # For SPA to catch all request by /index.html
  custom_error_response {
    #error_caching_min_ttl = 360
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    #error_caching_min_ttl = 360
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${local.fqdn.media_site}"
    #viewer_protocol_policy = "allow-all"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    cache_policy_id        = data.aws_cloudfront_cache_policy.managed_caching_optimized.id
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

# Create IAM poliocy document
data "aws_iam_policy_document" "s3_policy_static_site" {
  statement {
    #sid     = "PublicRead"
    sid     = "AllowCloudFrontAccess"
    effect  = "Allow"
    actions = ["s3:GetObject"]
    resources = [
      #aws_s3_bucket.static_site.arn,
      "${aws_s3_bucket.static_site.arn}/*"
    ]

    # Accept to access from CloudFront only
    principals {
      identifiers = [aws_cloudfront_origin_access_identity.static_site.iam_arn]
      type        = "AWS"
    }

    ## Accept to access from All
    #principals {
    #  identifiers = ["*"]
    #  type        = "*"
    #}
  }
}

data "aws_iam_policy_document" "s3_policy_media_site" {
  statement {
    #sid     = "PublicRead"
    sid     = "AllowCloudFrontAccess"
    effect  = "Allow"
    actions = ["s3:GetObject"]
    resources = [
      #aws_s3_bucket.media_site.arn,
      "${aws_s3_bucket.media_site.arn}/*"
    ]

    # Accept to access from CloudFront only
    principals {
      identifiers = [aws_cloudfront_origin_access_identity.media_site.iam_arn]
      type        = "AWS"
    }

    ## Accept to access from All
    #principals {
    #  identifiers = ["*"]
    #  type        = "*"
    #}
  }
}

# Related policy to bucket
resource "aws_s3_bucket_policy" "static_site" {
  provider = aws.site
  bucket   = aws_s3_bucket.static_site.id
  policy   = data.aws_iam_policy_document.s3_policy_static_site.json
}

resource "aws_s3_bucket_policy" "media_site" {
  provider = aws.site
  bucket   = aws_s3_bucket.media_site.id
  policy   = data.aws_iam_policy_document.s3_policy_media_site.json
}

## S3 for Static Website Hosting
resource "aws_s3_bucket" "static_site" {
  provider      = aws.site
  bucket        = local.bucket.static_site
  force_destroy = true # Set true, destroy bucket with objects

  acl = "private" # Accept to access from CloudFront only
  #acl = "public-read" # Accept to access to S3 Bucket from All

  #logging {
  #  target_bucket = aws_s3_bucket.accesslog_static_site.id
  #  target_prefix = "log/static/prd/s3/"
  #}

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "s3", "static_site"])
    ManagedBy = "terraform"
  }
}

resource "aws_s3_bucket" "media_site" {
  provider      = aws.site
  bucket        = local.bucket.media_site
  force_destroy = true # Set true, destroy bucket with objects

  acl = "private" # Accept to access from CloudFront only
  #acl = "public-read" # Accept to access to S3 Bucket from All

  #logging {
  #  target_bucket = aws_s3_bucket.accesslog_static_site.id
  #  target_prefix = "log/media/prd/s3/"
  #}

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "s3", "media_site"])
    ManagedBy = "terraform"
  }
}

# S3 Public Access Block
# Accept to access from All
resource "aws_s3_bucket_public_access_block" "static_site" {
  provider                = aws.site
  bucket                  = aws_s3_bucket.static_site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "media_site" {
  provider                = aws.site
  bucket                  = aws_s3_bucket.media_site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Cognito
resource "aws_cognito_user_pool" "default" {
  provider                 = aws.api
  name                     = join("-", [var.prj_prefix, "cognito-user-pool"])
  auto_verified_attributes = ["email"]
  alias_attributes         = ["email"]
  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
  }
  schema {
    attribute_data_type      = "String"
    name                     = "role"
    developer_only_attribute = false
    required                 = false
    mutable                  = true

    string_attribute_constraints {
      max_length = "64"
      #min_length = "1"
    }
  }
  schema {
    attribute_data_type      = "String"
    name                     = "acceptServiceIds"
    developer_only_attribute = false
    required                 = false
    mutable                  = true

    string_attribute_constraints {
      max_length = "128"
      #min_length = "1"
    }
  }
  username_configuration {
    case_sensitive = false
  }
  lifecycle {
    ignore_changes = [schema]
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
    #recovery_mechanism {
    #  name     = "verified_phone_number"
    #  priority = 2
    #}
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "cognito", "user", "pool"])
    ManagedBy = "terraform"
  }
}

resource "aws_cognito_user_pool_client" "default" {
  provider        = aws.api
  name            = join("-", [var.prj_prefix, "web_client"])
  user_pool_id    = aws_cognito_user_pool.default.id
  generate_secret = false
  explicit_auth_flows = [
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
}

resource "aws_cognito_identity_pool" "default" {
  provider                         = aws.api
  identity_pool_name               = join("-", [var.prj_prefix, "cognito-identity-pool"])
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.default.id
    provider_name           = aws_cognito_user_pool.default.endpoint
    server_side_token_check = false
  }

  #read_attributes = [
  #  "email",
  #  "custom:role",
  #]

  #write_attributes = [
  #  "email",
  #  "custom:role",
  #]

  tags = {
    Name      = join("-", [var.prj_prefix, "cognito", "identity", "pool"])
    ManagedBy = "terraform"
  }
}
