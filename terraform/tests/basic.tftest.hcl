run "validate_plan" {
  command = plan

  variables {
    aws_region    = "us-east-1"
    environment   = "test"
    project_name  = "platform-service"
    lambda_s3_key = "lambda/test.zip"
  }

  assert {
    condition     = output.function_name != ""
    error_message = "Function name should not be empty"
  }
}
