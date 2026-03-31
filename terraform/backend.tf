terraform {
  backend "s3" {
    bucket          = "elijah-terraform-state"
    workspace_key_prefix = "platform-service-idp"
    key             = "terraform.tfstate"
    region          = "us-east-2"
    dynamodb_table  = "elijah-terraform-lock-table"   
    encrypt        = true
  }
}
