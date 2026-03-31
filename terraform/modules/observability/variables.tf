variable "function_name" {
  description = "Lambda function name to monitor"
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "error_threshold" {
  description = "Error count threshold for alarm"
  type        = number
  default     = 0
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
