variable "github_repo" {
  description = "GitHub repository in format 'owner/repo'"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
