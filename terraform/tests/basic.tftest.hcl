run "validate_plan" {
  command = plan

  variables {
    aws_region    = "us-east-2"
    environment   = "test"
    project_name  = "platform-service"
    lambda_s3_key = "lambda/test.zip"
    alert_emails  = []
    github_repo   = "test-org/test-repo"
  }

  assert {
    condition     = output.function_name != ""
    error_message = "Function name should not be empty"
  }
}
