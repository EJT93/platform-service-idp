# --- Modules ---

module "s3" {
  source      = "../../modules/s3"
  bucket_name = "${var.project_name}-artifacts-${var.environment}"
  tags        = local.tags
}

module "dynamodb" {
  source     = "../../modules/dynamodb"
  table_name = "platform-services-${var.environment}"
  tags       = local.tags
}

module "iam" {
  source             = "../../modules/iam"
  function_name      = local.function_name
  dynamodb_table_arn = module.dynamodb.table_arn
  tags               = local.tags
}

module "lambda_api" {
  source              = "../../modules/lambda_api"
  function_name       = local.function_name
  lambda_role_arn     = module.iam.role_arn
  s3_bucket           = module.s3.bucket_name
  s3_key              = var.lambda_s3_key
  dynamodb_table_name = module.dynamodb.table_name
  tags                = local.tags
}

module "observability" {
  source        = "../../modules/observability"
  function_name = module.lambda_api.function_name
  tags          = local.tags
}
