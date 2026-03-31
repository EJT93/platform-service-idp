data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "audit" {
  name               = "${var.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "basic_execution" {
  role       = aws_iam_role.audit.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Read-only access for auditing AWS resources
data "aws_iam_policy_document" "audit_read" {
  statement {
    sid = "S3Audit"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucketEncryption",
      "s3:GetBucketPublicAccessBlock",
      "s3:GetBucketTagging",
      "s3:GetBucketLocation",
    ]
    resources = ["arn:aws:s3:::*"]
  }

  statement {
    sid = "DynamoDBAudit"
    actions = [
      "dynamodb:ListTables",
      "dynamodb:DescribeTable",
      "dynamodb:DescribeContinuousBackups",
    ]
    resources = ["*"]
  }

  statement {
    sid = "LambdaAudit"
    actions = [
      "lambda:ListFunctions",
      "lambda:GetFunction",
    ]
    resources = ["*"]
  }

  statement {
    sid = "CloudWatchLogsAudit"
    actions = [
      "logs:DescribeLogGroups",
    ]
    resources = ["*"]
  }

  # Write audit reports to S3
  statement {
    sid     = "AuditReportWrite"
    actions = ["s3:PutObject"]
    resources = [
      "${var.audit_s3_bucket_arn}/audit-reports/*",
    ]
  }
}

resource "aws_iam_role_policy" "audit_read" {
  name   = "${var.function_name}-audit-read"
  role   = aws_iam_role.audit.id
  policy = data.aws_iam_policy_document.audit_read.json
}
