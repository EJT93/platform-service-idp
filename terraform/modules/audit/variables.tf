variable "function_name" {
  description = "Audit Lambda function name"
  type        = string
}

variable "lambda_role_arn" {
  description = "IAM role ARN for the audit Lambda"
  type        = string
}

variable "s3_bucket" {
  description = "S3 bucket for deployment package"
  type        = string
}

variable "s3_key" {
  description = "S3 key for deployment package"
  type        = string
}

variable "audit_s3_bucket" {
  description = "S3 bucket to write audit reports to"
  type        = string
}

variable "api_id" {
  description = "API Gateway v2 API ID to attach routes to"
  type        = string
}

variable "api_execution_arn" {
  description = "API Gateway execution ARN for Lambda permission"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
