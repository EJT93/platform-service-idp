# --- Locals ---

locals {
  function_name = "${var.project_name}-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}