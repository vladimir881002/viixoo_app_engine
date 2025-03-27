terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.92.0"
    }
  }
  required_version = "~>1.11.2"
}

provider "aws" {
  region = "us-east-1"
  alias  = "s3-backend-us-east-1"
}