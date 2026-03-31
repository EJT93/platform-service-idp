output "subscription_arns" {
  value = { for email, sub in aws_sns_topic_subscription.email : email => sub.arn }
}
