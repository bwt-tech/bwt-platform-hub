resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/ecs/api-bwt-hub"
  retention_in_days = 1
}
