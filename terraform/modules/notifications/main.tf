resource "aws_sns_topic_subscription" "email" {
  for_each  = toset(var.alert_emails)
  topic_arn = var.sns_topic_arn
  protocol  = "email"
  endpoint  = each.value
}
