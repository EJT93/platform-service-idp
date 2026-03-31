resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = var.billing_mode
  hash_key     = "service_id"

  attribute {
    name = "service_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = var.enable_pitr
  }

  tags = var.tags
}
