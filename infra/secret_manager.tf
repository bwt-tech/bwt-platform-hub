resource "aws_secretsmanager_secret" "secrets_bwt" {
  name = "secrets_bwt"
}

resource "aws_secretsmanager_secret" "datadog_logs_api_key" {
  name = "datadog_logs_api_key"
}