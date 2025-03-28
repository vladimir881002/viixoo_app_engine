locals {
  aws_zone_names = {
    "us-east-1" = "us-east-1"
  }

  aws_subnet_zone = "us-east-1a"

  default_tags = {
    "owner"    = "viixoo"
    "customer" = "hemago"
    "repo"     = "github.com:viixoo/viixoo_hemago_mrp_app"
  }
}
