variable "aws_region" {
  description = "Region chosen by the account owner."
  type        = string
}

variable "bucket_name" {
  description = "Globally unique bucket name; no default to prevent accidental provisioning."
  type        = string
  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63 && can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.bucket_name))
    error_message = "Use a valid globally unique S3 bucket name."
  }
}
