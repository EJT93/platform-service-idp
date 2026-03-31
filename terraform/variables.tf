# --- Variables ---

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
}

variable "lambda_s3_key" {
  description = "S3 key for the Lambda deployment package"
  type        = string
  default     = "lambda/package.zip"
}
