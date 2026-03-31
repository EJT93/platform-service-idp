variable "sns_topic_arn" {
  description = "ARN of the SNS topic to subscribe to"
  type        = string
}

variable "alert_emails" {
  description = "List of email addresses to receive alarm notifications"
  type        = list(string)
}
