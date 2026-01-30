# Helm AI Infrastructure as Code - Terraform Configuration
# Main configuration file for Helm AI production infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.0"
    }
    datadog = {
      source  = "DataDog/datadog"
      version = "~> 3.0"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    Environment = var.environment
    Project     = "helm-ai"
    ManagedBy   = "terraform"
  }
}

# Configure Kubernetes Provider
provider "kubernetes" {
  config_path = var.kubeconfig_path
  host                   = var.kubernetes_host
  token                  = var.kubernetes_token
  cluster_ca_certificate = var.kubernetes_ca_certificate
}

# Configure Helm Provider
provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
    host                   = var.kubernetes_host
    token                  = var.kubernetes_token
    cluster_ca_certificate = var.kubernetes_ca_certificate
  }
}

# Configure Vault Provider
provider "vault" {
  address = var.vault_address
  token   = var.vault_token
}

# Configure Datadog Provider
provider "datadog" {
  api_key = var.datadog_api_key
  site    = var.datadog_site
}

# Random resources for unique identifiers
resource "random_id" "suffix" {
  byte_length = 4
}

# VPC Configuration
resource "aws_vpc" "helm_ai_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "helm-ai-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "helm_ai_igw" {
  vpc_id = aws_vpc.helm_ai_vpc.id
  
  tags = {
    Name = "helm-ai-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnets" {
  count = length(var.public_subnet_cidrs)
  
  vpc_id                  = aws_vpc.helm_ai_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "helm-ai-public-${count.index + 1}"
    Type = "Public"
  }
}

# Private Subnets
resource "aws_subnet" "private_subnets" {
  count = length(var.private_subnet_cidrs)
  
  vpc_id            = aws_vpc.helm_ai_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "helm-ai-private-${count.index + 1}"
    Type = "Private"
  }
}

# Database Subnets
resource "aws_subnet" "database_subnets" {
  count = length(var.database_subnet_cidrs)
  
  vpc_id            = aws_vpc.helm_ai_vpc.id
  cidr_block        = var.database_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "helm-ai-database-${count.index + 1}"
    Type = "Database"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "helm_ai" {
  name     = "helm-ai-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version
  
  vpc_config {
    subnet_ids = concat(aws_subnet.private_subnets[*].id, aws_subnet.public_subnets[*].id)
  }
  
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy,
    aws_cloudwatch_log_group.eks_cluster
  ]
  
  tags = {
    Name = "helm-ai-eks-cluster"
  }
}

# EKS Node Groups
resource "aws_eks_node_group" "helm_ai_workers" {
  cluster_name    = aws_eks_cluster.helm_ai.name
  node_group_name = "helm-ai-workers"
  node_role_arn   = aws_iam_role.eks_node_group.arn
  subnet_ids      = aws_subnet.private_subnets[*].id
  
  scaling_config {
    desired_size = var.desired_node_count
    max_size     = var.max_node_count
    min_size     = var.min_node_count
  }
  
  instance_types = [var.instance_type]
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy
  ]
  
  tags = {
    Name = "helm-ai-worker-nodes"
  }
}

# RDS Database
resource "aws_db_subnet_group" "helm_ai_db" {
  name       = "helm-ai-db-subnet-group"
  subnet_ids = aws_subnet.database_subnets[*].id
  
  tags = {
    Name = "helm-ai-db-subnet-group"
  }
}

resource "aws_security_group" "helm_ai_db" {
  name        = "helm-ai-db-sg"
  description = "Security group for Helm AI database"
  vpc_id      = aws_vpc.helm_ai_vpc.id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.helm_ai_vpc.cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "helm-ai-db-sg"
  }
}

resource "aws_db_instance" "helm_ai_postgres" {
  identifier     = "helm-ai-postgres"
  engine         = "postgres"
  engine_version  = "14.9"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "helm_ai"
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name = aws_db_subnet_group.helm_ai_db.name
  vpc_security_group_ids = [aws_security_group.helm_ai_db.id]
  
  backup_retention_period = var.db_backup_retention_period
  backup_window          = "03:00-04:00"
  delete_automated_backup = false
  skip_final_snapshot     = false
  
  tags = {
    Name = "helm-ai-postgres"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "helm_ai_redis" {
  name       = "helm-ai-redis-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id
  
  tags = {
    Name = "helm-ai-redis-subnet-group"
  }
}

resource "aws_security_group" "helm_ai_redis" {
  name        = "helm-ai-redis-sg"
  description = "Security group for Helm AI Redis"
  vpc_id      = aws_vpc.helm_ai_vpc.id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.helm_ai_vpc.cidr_block]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "helm-ai-redis-sg"
  }
}

resource "aws_elasticache_cluster" "helm_ai_redis" {
  cluster_id           = "helm-ai-redis"
  engine               = "redis"
  engine_version        = "7.0"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_nodes
  parameter_group_name = aws_elasticache_parameter_group.helm_ai_redis.name
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.helm_ai_redis.name
  security_group_ids   = [aws_security_group.helm_ai_redis.id]
  
  at_rest_encryption = {
    encryption_at_rest_type = "KMS"
    kms_key_id          = aws_kms_key.helm_ai_encryption.arn
  }
  
  tags = {
    Name = "helm-ai-redis"
  }
}

# S3 Buckets
resource "aws_s3_bucket" "helm_ai_storage" {
  bucket = "helm-ai-storage-${random_id.suffix.result}"
  
  tags = {
    Name = "helm-ai-storage"
  }
}

resource "aws_s3_bucket_versioning" "helm_ai_storage_versioning" {
  bucket = aws_s3_bucket.helm_ai_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "helm_ai_storage_encryption" {
  bucket = aws_s3_bucket.helm_ai_storage.id
  
  rule {
    apply_server_side_encryption_by_default = {
      sse_algorithm = "AES256"
    }
  }
}

# Application Load Balancer
resource "aws_lb" "helm_ai_alb" {
  name               = "helm-ai-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.helm_ai_alb.id]
  subnets            = aws_subnet.public_subnets[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Name = "helm-ai-alb"
  }
}

resource "aws_lb_target_group" "helm_ai_tg" {
  name     = "helm-ai-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.helm_ai_vpc.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Name = "helm-ai-tg"
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "helm_ai_asg" {
  name                = "helm-ai-asg"
  vpc_zone_identifier  = aws_subnet.private_subnets[*].availability_zone
  target_group_arns   = [aws_lb_target_group.helm_ai_tg.arn]
  health_check_type   = "EC2"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.helm_ai.id
    version = "$Latest"
  }
  
  min_size         = var.min_node_count
  max_size         = var.max_node_count
  desired_capacity = var.desired_node_count
  
  tag {
    key                 = "Name"
    value               = "helm-ai-asg"
    propagate_at_launch = true
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "eks_cluster" {
  name = "/aws/eks/cluster/helm-ai"
  
  tags = {
    Name = "helm-ai-eks-logs"
  }
}

# KMS Key for encryption
resource "aws_kms_key" "helm_ai_encryption" {
  description             = "KMS key for Helm AI encryption"
  deletion_window_in_days = 7
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.account_id}:root"
        }
        Action   = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = {
    Name = "helm-ai-encryption-key"
  }
}

# Helm Chart for Helm AI
resource "helm_release" "helm_ai" {
  name       = "helm-ai"
  repository = "https://helm-ai.github.io/helm-charts"
  chart      = "helm-ai"
  version    = var.helm_ai_chart_version
  
  namespace = "helm-ai"
  
  set {
    name  = "image.tag"
    value = var.helm_ai_image_tag
  }
  
  set {
    name  = "service.type"
    value = "LoadBalancer"
  }
  
  set {
    name  = "resources.requests.cpu"
    value = "500m"
  }
  
  set {
    name  = "resources.requests.memory"
    value = "1Gi"
  }
  
  set {
    name  = "resources.limits.cpu"
    value = "1000m"
  }
  
  set {
    name  = "resources.limits.memory"
    value = "2Gi"
  }
  
  depends_on = [
    aws_eks_cluster.helm_ai,
    aws_eks_node_group.helm_ai_workers
  ]
}

# Datadog Monitors
resource "datadog_monitor" "helm_ai_cpu" {
  name  = "Helm AI CPU Usage"
  type  = "metric alert"
  query = "avg(last_5m):avg:system.cpu.total:avg:system.cpu.total:helm-ai"
  
  message = "Helm AI CPU usage is {{#threshold}}"
  tags    = ["helm-ai", "cpu", "monitoring"]
  
  monitor_thresholds {
    critical {
      operator = ">"
      value    = 80
    }
    warning {
      operator = ">"
      value    = 60
    }
  }
}

resource "datadog_monitor" "helm_ai_memory" {
  name  = "Helm AI Memory Usage"
  type  = "metric alert"
  query = "avg(last_5m):avg:system.memory.used:avg:system.memory.used:helm-ai"
  
  message = "Helm AI memory usage is {{#threshold}}"
  tags    = ["helm-ai", "memory", "monitoring"]
  
  monitor_thresholds {
    critical {
      operator = ">"
      value    = 85
    }
    warning {
      operator = ">"
      value    = 70
    }
  }
}

# Vault Configuration
resource "vault_namespace" "helm_ai" {
  path = "helm-ai"
}

resource "vault_policy" "helm_ai_policy" {
  name = "helm-ai-policy"
  
  policy = jsonencode({
    path = {
      "helm-ai/*" = {
        capabilities = ["create", "read", "update", "delete", "list", "sudo"]
      }
    }
  })
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Output values
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.helm_ai.endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.helm_ai.name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.helm_ai_vpc.id
}

output "database_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.helm_ai_postgres.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.helm_ai_redis.cache_nodes[0].address
}

output "load_balancer_dns" {
  description = "Application load balancer DNS name"
  value       = aws_lb.helm_ai_alb.dns_name
}

output "storage_bucket" {
  description = "S3 storage bucket name"
  value       = aws_s3_bucket.helm_ai_storage.bucket
}

output "kms_key_id" {
  description = "KMS encryption key ID"
  value       = aws_kms_key.helm_ai_encryption.key_id
}
