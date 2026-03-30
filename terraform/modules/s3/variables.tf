variable "bucket_name" {
  description = "S3 bucket name for deployment artifacts"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
