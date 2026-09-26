variable "vpc_id" {
  type = string
}

variable "cluster_id" {
  type = string
}

variable "port" {
  type = string
}

variable "role_ecs_name" {
  type = string
}

# ============================================================
# Database — SSM Parameter ARNs (vindos da infra base)
# ============================================================

variable "db_host_ssm_arn" {
  type        = string
  description = "ARN do SSM Parameter com o host do banco de dados"
}

variable "db_port_ssm_arn" {
  type        = string
  description = "ARN do SSM Parameter com a porta do banco de dados"
}

variable "db_name_ssm_arn" {
  type        = string
  description = "ARN do SSM Parameter com o nome do banco de dados"
}

variable "db_user_ssm_arn" {
  type        = string
  description = "ARN do SSM Parameter com o usuário do banco de dados"
}

variable "db_password_ssm_arn" {
  type        = string
  description = "ARN do SSM Parameter (SecureString) com a senha do banco de dados"
}

variable "private_sg_id" {
  type        = string
  description = "ID do Security Group privado das ECS Tasks (exportado pela infra base). Deve ser o SG autorizado na regra de ingress do RDS."
}

variable "env" {
  type        = string
  description = "Environemtn"
}
