data "aws_ecr_image" "service_image" {
  repository_name = "bwt-platform-hub-${var.env}"
  most_recent     = true
}

resource "aws_ecs_task_definition" "api-bwt-hub" {
  family                   = "api-bwt-hub"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.role_ecs.arn
  task_role_arn            = aws_iam_role.role_ecs.arn

  container_definitions = jsonencode([
    {
      name      = "task-def-dev"
      image     = data.aws_ecr_image.service_image.image_uri
      cpu       = 256
      memory    = 512
      essential = true

      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]

      # --------------------------------------------------------
      # Credenciais do banco injetadas de forma segura via SSM.
      # O ECS resolve os valores em runtime — nunca ficam em
      # texto plano nos logs ou no state do Terraform.
      # A aplicação monta a DATABASE_URL a partir dessas variáveis
      # individuais quando DATABASE_URL não estiver definida.
      # --------------------------------------------------------
      secrets = [
        {
          name      = "DB_HOST"
          valueFrom = var.db_host_ssm_arn
        },
        {
          name      = "DB_PORT"
          valueFrom = var.db_port_ssm_arn
        },
        {
          name      = "DB_NAME"
          valueFrom = var.db_name_ssm_arn
        },
        {
          name      = "DB_USER"
          valueFrom = var.db_user_ssm_arn
        },
        {
          name      = "DB_PASSWORD"
          valueFrom = var.db_password_ssm_arn
        }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f -k http://localhost:8080/health || exit 1"]
        interval    = 300
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app_logs.name
          awslogs-region        = "us-east-1"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}
