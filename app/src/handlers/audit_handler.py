"""Platform audit handler — aggregates operational data across AWS resources."""

import json
import os
from datetime import datetime, timezone

import boto3
from utils.logger import get_logger


def handler(event: dict, context) -> dict:
    """Lambda handler for platform audit reports."""
    request_id = getattr(context, "aws_request_id", "unknown")
    function_name = getattr(context, "function_name", "unknown")
    logger = get_logger(__name__, request_id=request_id, function_name=function_name)

    http_method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    logger.info("Received %s %s", http_method, path)

    if http_method != "GET" or path != "/platform/audit":
        return _response(404, {"error": "Route not found"})

    try:
        report = _build_audit_report(logger)
        _write_to_s3(report, logger)
        return _response(200, report)
    except Exception:
        logger.exception("Audit report failed")
        return _response(500, {"error": "Internal server error"})


def _build_audit_report(logger) -> dict:
    """Collect operational data from S3, DynamoDB, Lambda, and CloudWatch."""
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "s3_buckets": _audit_s3(logger),
        "dynamodb_tables": _audit_dynamodb(logger),
        "lambda_functions": _audit_lambda(logger),
        "cloudwatch_log_groups": _audit_log_groups(logger),
    }
    total_issues = sum(
        1 for b in report["s3_buckets"] if not b.get("encryption_enabled")
    ) + sum(
        1 for t in report["dynamodb_tables"] if not t.get("pitr_enabled")
    ) + sum(
        1 for lg in report["cloudwatch_log_groups"] if lg.get("retention_days") is None
    )
    report["summary"] = {
        "total_s3_buckets": len(report["s3_buckets"]),
        "total_dynamodb_tables": len(report["dynamodb_tables"]),
        "total_lambda_functions": len(report["lambda_functions"]),
        "total_log_groups": len(report["cloudwatch_log_groups"]),
        "issues_found": total_issues,
    }
    return report


def _audit_s3(logger) -> list[dict]:
    """Audit S3 buckets for encryption and public access settings."""
    s3 = boto3.client("s3")
    results = []
    try:
        buckets = s3.list_buckets().get("Buckets", [])
        for bucket in buckets:
            name = bucket["Name"]
            info = {"name": name, "created": bucket["CreationDate"].isoformat()}
            try:
                enc = s3.get_bucket_encryption(Bucket=name)
                rules = enc.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
                algo = rules[0]["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"] if rules else None
                info["encryption_enabled"] = True
                info["encryption_algorithm"] = algo
            except s3.exceptions.ClientError:
                info["encryption_enabled"] = False
                info["encryption_algorithm"] = None
            try:
                pab = s3.get_public_access_block(Bucket=name)
                cfg = pab.get("PublicAccessBlockConfiguration", {})
                info["public_access_blocked"] = all([
                    cfg.get("BlockPublicAcls", False),
                    cfg.get("BlockPublicPolicy", False),
                    cfg.get("IgnorePublicAcls", False),
                    cfg.get("RestrictPublicBuckets", False),
                ])
            except Exception:
                info["public_access_blocked"] = False
            results.append(info)
    except Exception:
        logger.exception("Failed to audit S3")
    return results


def _audit_dynamodb(logger) -> list[dict]:
    """Audit DynamoDB tables for backup and encryption settings."""
    ddb = boto3.client("dynamodb")
    results = []
    try:
        tables = ddb.list_tables().get("TableNames", [])
        for table_name in tables:
            desc = ddb.describe_table(TableName=table_name)["Table"]
            pitr = ddb.describe_continuous_backups(TableName=table_name)
            pitr_status = pitr.get("ContinuousBackupsDescription", {}).get(
                "PointInTimeRecoveryDescription", {}
            ).get("PointInTimeRecoveryStatus", "DISABLED")
            sse = desc.get("SSEDescription", {})
            results.append({
                "name": table_name,
                "billing_mode": desc.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
                "item_count": desc.get("ItemCount", 0),
                "pitr_enabled": pitr_status == "ENABLED",
                "encryption_type": sse.get("SSEType", "DEFAULT"),
            })
    except Exception:
        logger.exception("Failed to audit DynamoDB")
    return results


def _audit_lambda(logger) -> list[dict]:
    """Audit Lambda functions for runtime, memory, and timeout."""
    lam = boto3.client("lambda")
    results = []
    try:
        paginator = lam.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page.get("Functions", []):
                results.append({
                    "name": fn["FunctionName"],
                    "runtime": fn.get("Runtime", "N/A"),
                    "memory_mb": fn.get("MemorySize"),
                    "timeout_sec": fn.get("Timeout"),
                    "last_modified": fn.get("LastModified"),
                    "code_size_bytes": fn.get("CodeSize"),
                })
    except Exception:
        logger.exception("Failed to audit Lambda")
    return results


def _audit_log_groups(logger) -> list[dict]:
    """Audit CloudWatch Log Groups for retention settings."""
    logs = boto3.client("logs")
    results = []
    try:
        paginator = logs.get_paginator("describe_log_groups")
        for page in paginator.paginate():
            for lg in page.get("logGroups", []):
                results.append({
                    "name": lg["logGroupName"],
                    "retention_days": lg.get("retentionInDays"),
                    "stored_bytes": lg.get("storedBytes", 0),
                })
    except Exception:
        logger.exception("Failed to audit CloudWatch Logs")
    return results


def _write_to_s3(report: dict, logger) -> None:
    """Write audit report to S3 artifacts bucket."""
    bucket = os.environ.get("AUDIT_S3_BUCKET")
    if not bucket:
        logger.warning("AUDIT_S3_BUCKET not set, skipping S3 write")
        return
    s3 = boto3.client("s3")
    key = f"audit-reports/{report['generated_at'][:10]}/audit-{report['generated_at']}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(report, indent=2, default=str),
        ContentType="application/json",
    )
    logger.info("Audit report written to s3://%s/%s", bucket, key)


def _response(status_code: int, body) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, indent=2, default=str) if body else "",
    }
