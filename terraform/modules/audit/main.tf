resource "aws_lambda_function" "audit" {
  function_name = var.function_name
  role          = var.lambda_role_arn
  handler       = "handlers.audit_handler.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 256

  s3_bucket = var.s3_bucket
  s3_key    = var.s3_key

  environment {
    variables = {
      AUDIT_S3_BUCKET = var.audit_s3_bucket
    }
  }

  tags = var.tags
}

# Log group with retention for audit Lambda
resource "aws_cloudwatch_log_group" "audit" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
  tags              = var.tags
}

# Route: GET /platform/audit
resource "aws_apigatewayv2_integration" "audit" {
  api_id                 = var.api_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.audit.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "audit" {
  api_id    = var.api_id
  route_key = "GET /platform/audit"
  target    = "integrations/${aws_apigatewayv2_integration.audit.id}"
}

resource "aws_lambda_permission" "apigw_audit" {
  statement_id  = "AllowAPIGatewayAudit"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.audit.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_execution_arn}/*/*"
}
