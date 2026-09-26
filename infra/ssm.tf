resource "aws_ssm_parameter" "scheduler_enabled" {
  name        = "/bwt/scheduler/enabled"
  description = "Enable or disable the background synchronization scheduler"
  type        = "String"
  value       = "false"
  overwrite   = false
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "scheduler_cron" {
  name        = "/bwt/scheduler/cron"
  description = "Cron expression for the synchronization job"
  type        = "String"
  overwrite   = false
  value       = "* 5-16 * * *"
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "scheduler_batch_size" {
  name        = "/bwt/scheduler/batch_size"
  description = "Maximum number of deals to process per synchronization run"
  type        = "String"
  value       = "1"
  overwrite   = false
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "octadesk_key_mendoza" {
  name        = "/bwt/octadesk/keys/mendoza"
  description = "Octadesk API Key for Mendoza pipeline agent"
  type        = "SecureString"
  value       = "placeholder_key_mendoza"
  overwrite   = false
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "octadesk_key_salta" {
  name        = "/bwt/octadesk/keys/salta"
  description = "Octadesk API Key for Salta pipeline agent"
  type        = "SecureString"
  value       = "placeholder_key_salta"
  overwrite   = false
  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "octadesk_key_serra_gaucha" {
  name        = "/bwt/octadesk/keys/serra_gaucha"
  description = "Octadesk API Key for Serra Gaúcha pipeline agent"
  type        = "SecureString"
  value       = "placeholder_key_serra_gaucha"
  overwrite   = false
  lifecycle {
    ignore_changes = [value]
  }
}

