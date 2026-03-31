# --- Outputs ---

output "api_endpoint" {
  value = module.lambda_api.api_endpoint
}

output "function_name" {
  value = module.lambda_api.function_name
}

output "dynamodb_table" {
  value = module.dynamodb.table_name
}

output "s3_bucket" {
  value = module.s3.bucket_name
}

output "github_actions_role_arn" {
  value = module.github_oidc.role_arn
}
