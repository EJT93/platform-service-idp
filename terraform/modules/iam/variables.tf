variable "function_name" {
  description = "Lambda function name (used for role naming)"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table to grant access to"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}

variable "ssm_parameter_arns" {
  description = "ARNs of SSM parameters the Lambda can read"
  type        = list(string)
  default     = []
}
