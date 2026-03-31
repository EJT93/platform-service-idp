output "role_arn" {
  value = aws_iam_role.audit.arn
}

output "role_name" {
  value = aws_iam_role.audit.name
}
