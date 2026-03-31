variable "function_name" {
  description = "Audit function name for role naming"
  type        = string
}

variable "audit_s3_bucket_arn" {
  description = "ARN of the S3 bucket for writing audit reports"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
