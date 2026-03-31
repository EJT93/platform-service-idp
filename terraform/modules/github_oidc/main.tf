# GitHub OIDC Identity Provider
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
  tags            = var.tags
}

# Trust policy: allow GitHub Actions from this repo to assume the role
data "aws_iam_policy_document" "github_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:*"]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = "github-actions-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json
  tags               = var.tags
}

# Permissions for Terraform operations — scoped, no wildcards
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
}

data "aws_iam_policy_document" "deploy" {
  # S3 — state bucket + artifacts bucket
  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:DeleteObject",
      "s3:GetBucketVersioning",
      "s3:GetBucketPolicy",
      "s3:GetBucketAcl",
      "s3:GetBucketCORS",
      "s3:GetBucketLocation",
      "s3:GetBucketLogging",
      "s3:GetBucketTagging",
      "s3:GetBucketWebsite",
      "s3:GetBucketObjectLockConfiguration",
      "s3:GetAccelerateConfiguration",
      "s3:GetBucketRequestPayment",
      "s3:GetLifecycleConfiguration",
      "s3:GetReplicationConfiguration",
      "s3:GetEncryptionConfiguration",
      "s3:GetBucketPublicAccessBlock",
      "s3:PutBucketVersioning",
      "s3:PutBucketPolicy",
      "s3:PutEncryptionConfiguration",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutBucketTagging",
      "s3:CreateBucket",
    ]
    resources = [
      "arn:aws:s3:::elijah-terraform-state",
      "arn:aws:s3:::elijah-terraform-state/*",
      "arn:aws:s3:::platform-service-artifacts-*",
      "arn:aws:s3:::platform-service-artifacts-*/*",
    ]
  }

  # DynamoDB — state lock table + app table
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
      "dynamodb:DescribeTable",
      "dynamodb:CreateTable",
      "dynamodb:DeleteTable",
      "dynamodb:TagResource",
      "dynamodb:UntagResource",
      "dynamodb:ListTagsOfResource",
      "dynamodb:UpdateContinuousBackups",
      "dynamodb:DescribeContinuousBackups",
      "dynamodb:DescribeTimeToLive",
    ]
    resources = [
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/elijah-terraform-lock-table",
      "arn:aws:dynamodb:${local.region}:${local.account_id}:table/platform-services-*",
    ]
  }

  # Lambda
  statement {
    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
      "lambda:DeleteFunction",
      "lambda:GetFunction",
      "lambda:GetFunctionConfiguration",
      "lambda:ListVersionsByFunction",
      "lambda:GetPolicy",
      "lambda:AddPermission",
      "lambda:RemovePermission",
      "lambda:TagResource",
      "lambda:UntagResource",
      "lambda:ListTags",
    ]
    resources = [
      "arn:aws:lambda:${local.region}:${local.account_id}:function:platform-service-*",
    ]
  }

  # API Gateway v2
  statement {
    actions = [
      "apigateway:GET",
      "apigateway:POST",
      "apigateway:PUT",
      "apigateway:PATCH",
      "apigateway:DELETE",
      "apigateway:TagResource",
    ]
    resources = [
      "arn:aws:apigateway:${local.region}::/apis",
      "arn:aws:apigateway:${local.region}::/apis/*",
    ]
  }

  # IAM — manage Lambda execution role
  statement {
    actions = [
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:GetRole",
      "iam:PassRole",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListRolePolicies",
      "iam:ListInstanceProfilesForRole",
    ]
    resources = [
      "arn:aws:iam::${local.account_id}:role/platform-service-*",
      "arn:aws:iam::${local.account_id}:role/github-actions-deploy",
    ]
  }

  # IAM OIDC Provider — manage the GitHub OIDC provider
  statement {
    actions = [
      "iam:GetOpenIDConnectProvider",
      "iam:CreateOpenIDConnectProvider",
      "iam:DeleteOpenIDConnectProvider",
      "iam:TagOpenIDConnectProvider",
      "iam:UntagOpenIDConnectProvider",
      "iam:ListOpenIDConnectProviderTags",
    ]
    resources = [
      "arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com",
    ]
  }

  # CloudWatch Logs
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:DescribeLogGroups",
      "logs:PutRetentionPolicy",
      "logs:TagLogGroup",
      "logs:UntagLogGroup",
      "logs:ListTagsLogGroup",
      "logs:TagResource",
      "logs:UntagResource",
      "logs:ListTagsForResource",
    ]
    resources = [
      "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/platform-service-*",
      "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/lambda/platform-service-*:*",
    ]
  }

  # CloudWatch Alarms
  statement {
    actions = [
      "cloudwatch:PutMetricAlarm",
      "cloudwatch:DeleteAlarms",
      "cloudwatch:DescribeAlarms",
      "cloudwatch:ListTagsForResource",
      "cloudwatch:TagResource",
      "cloudwatch:UntagResource",
    ]
    resources = [
      "arn:aws:cloudwatch:${local.region}:${local.account_id}:alarm:platform-service-*",
    ]
  }

  # SNS
  statement {
    actions = [
      "sns:CreateTopic",
      "sns:DeleteTopic",
      "sns:GetTopicAttributes",
      "sns:SetTopicAttributes",
      "sns:TagResource",
      "sns:UntagResource",
      "sns:ListTagsForResource",
      "sns:Subscribe",
      "sns:Unsubscribe",
      "sns:GetSubscriptionAttributes",
    ]
    resources = [
      "arn:aws:sns:${local.region}:${local.account_id}:platform-service-*",
    ]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "github-actions-deploy-policy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.deploy.json
}
