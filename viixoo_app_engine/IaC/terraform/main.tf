terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.92.0"
    }
  }
  required_version = "~>1.11.2"

  # Configure the S3 backend for state storage
  backend "s3" {
    bucket       = "viixoo-hemago-terraform-state" # Replace with your bucket name
    key          = "terraform.tfstate"             # Key for the state file
    region       = "us-east-1"                     # Replace with your region
    use_lockfile = true
    encrypt      = true # Enable server-side encryption
  }

}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = local.default_tags
  }
}