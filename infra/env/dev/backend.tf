terraform {
  backend "s3" {
    bucket = "bwtech-tfstate-dev"
    key    = "application-terraform.tfstate"
    region = "us-east-1"
    use_lockfile = true
  }
}