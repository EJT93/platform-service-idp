resource "aws_lambda_function" "api" {
  function_name = var.function_name
  role          = var.lambda_role_arn
  handler       = "handlers.service_handler.handler"
  runtime       = "python3.12"
  timeout       = var.timeout
  memory_size   = var.memory_size

  s3_bucket = var.s3_bucket
  s3_key    = var.s3_key

  environment {
    variables = {
      DYNAMODB_TABLE_SSM = var.dynamodb_table_ssm_param
      LOG_LEVEL          = var.log_level
    }
  }

  tags = var.tags
}

resource "aws_apigatewayv2_api" "api" {
  name          = "${var.function_name}-api"
  protocol_type = "HTTP"
  tags          = var.tags
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
