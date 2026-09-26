locals {
  env           = "dev"
  region        = "us-east-1"
  port          = "8080"
  cluster_id    = "bwt-ecs-cluster-dev"
  role_ecs_name = "role_task_ecs"
  vpc_id        = "vpc-0eb9910fa39036c4e"
  # Security Group das ECS Tasks autorizado no ingress do RDS.
  # A infra base não exporta este output via remote state, por isso é fixo aqui.
  private_sg_id = "sg-0e76786baedd6ae4f"
}

# ============================================================
# Remote State — Infraestrutura Base (infra-ecs-cluster)
# Permite referenciar os outputs do RDS sem hardcode
# ============================================================

data "terraform_remote_state" "base_infra" {
  backend = "s3"
  config = {
    bucket = "bwtech-tfstate-dev"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

# ============================================================
# Locals — ARNs dos SSM Parameters do banco
# O account_id é obtido dinamicamente para evitar hardcode
# ============================================================

data "aws_caller_identity" "current" {}

locals {
  ssm_base_arn = "arn:aws:ssm:${local.region}:${data.aws_caller_identity.current.account_id}:parameter"
}

module "dev" {
  source        = "../../"
  cluster_id    = local.cluster_id
  role_ecs_name = local.role_ecs_name
  vpc_id        = local.vpc_id
  port          = local.port
  env          = local.env

  # Parâmetros SSM do banco provisionados pela infra base
  db_host_ssm_arn     = "${local.ssm_base_arn}/bwt/${local.env}/database/host"
  db_port_ssm_arn     = "${local.ssm_base_arn}/bwt/${local.env}/database/port"
  db_name_ssm_arn     = "${local.ssm_base_arn}/bwt/${local.env}/database/name"
  db_user_ssm_arn     = "${local.ssm_base_arn}/bwt/${local.env}/database/username"
  db_password_ssm_arn = "${local.ssm_base_arn}/bwt/${local.env}/database/password"

  # Security Group privado das ECS Tasks (origens permitidas pelo RDS)
  private_sg_id = local.private_sg_id
}
