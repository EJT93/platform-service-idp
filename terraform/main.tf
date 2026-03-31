# --- Modules ---

# SSM Parameter Store — sensitive/config values
resource "aws_ssm_parameter" "dynamodb_table" {
  name  = "/${var.project_name}/${var.environment}/dynamodb-table-name"
  type  = "String"
  value = module.dynamodb.table_name
  tags  = local.tags
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = "${var.project_name}-artifacts-${var.environment}"
  tags        = local.tags
}

module "dynamodb" {
  source     = "./modules/dynamodb"
  table_name = "platform-services-${var.environment}"
  tags       = local.tags
}

module "iam" {
  source             = "./modules/iam"
  function_name      = local.function_name
  dynamodb_table_arn = module.dynamodb.table_arn
  ssm_parameter_arns = [aws_ssm_parameter.dynamodb_table.arn]
  tags               = local.tags
}

module "lambda_api" {
  source                   = "./modules/lambda_api"
  function_name            = local.function_name
  lambda_role_arn          = module.iam.role_arn
  s3_bucket                = module.s3.bucket_name
  s3_key                   = var.lambda_s3_key
  dynamodb_table_ssm_param = aws_ssm_parameter.dynamodb_table.name
  tags                     = local.tags
}

module "observability" {
  source        = "./modules/observability"
  function_name = module.lambda_api.function_name
  tags          = local.tags
}

module "notifications" {
  source        = "./modules/notifications"
  sns_topic_arn = module.observability.sns_topic_arn
  alert_emails  = var.alert_emails
}

module "github_oidc" {
  source      = "./modules/github_oidc"
  github_repo = var.github_repo
  tags        = local.tags
}

module "audit_iam" {
  source              = "./modules/audit_iam"
  function_name       = "${local.function_name}-audit"
  audit_s3_bucket_arn = module.s3.bucket_arn
  tags                = local.tags
}

module "audit" {
  source            = "./modules/audit"
  function_name     = "${local.function_name}-audit"
  lambda_role_arn   = module.audit_iam.role_arn
  s3_bucket         = module.s3.bucket_name
  s3_key            = var.lambda_s3_key
  audit_s3_bucket   = module.s3.bucket_name
  api_id            = module.lambda_api.api_id
  api_execution_arn = module.lambda_api.api_execution_arn
  tags              = local.tags
}
