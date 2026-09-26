resource "aws_ecs_service" "api-hub-service" {
  name                              = "api-hub-service"
  cluster                           = var.cluster_id
  task_definition                   = aws_ecs_task_definition.api-bwt-hub.arn
  desired_count                     = 1
  health_check_grace_period_seconds = 0
  force_new_deployment              = true

  # --------------------------------------------------------
  # Security Group: deve ser o 'private_sg_id' exportado pela
  # infra base — é ele que está na regra de ingress do RDS.
  # O SG anterior (sg-0cb0f84a028f10114) era hardcoded e pode
  # não ser o SG autorizado a conectar no banco.
  # --------------------------------------------------------
  network_configuration {
    subnets          = ["subnet-0e3d422f644482872", "subnet-0fcae2af8a71568c7"]
    security_groups  = [var.private_sg_id]
    assign_public_ip = true # Necessário para pull de imagens sem NAT Gateway
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

