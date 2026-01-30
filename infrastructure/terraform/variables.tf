# Terraform Variables for Helm AI Infrastructure

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = can(regex("^(dev|staging|production)$", var.environment))
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.100.0/24", "10.0.110.0/24", "10.0.120.0/24"]
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
  default     = "m5.large"
}

variable "min_node_count" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "max_node_count" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "desired_node_count" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS database (GB)"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS database (GB)"
  type        = number
  default     = 1000
}

variable "db_username" {
  description = "RDS database username"
  type        = string
  default     = "helm_ai_admin"
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

variable "db_backup_retention_period" {
  description = "RDS backup retention period in days"
  type        = number
  default     = 7
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 2
}

variable "helm_ai_chart_version" {
  description = "Helm AI Helm chart version"
  type        = string
  default     = "1.0.0"
}

variable "helm_ai_image_tag" {
  description = "Helm AI Docker image tag"
  type        = string
  default     = "latest"
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kubernetes_host" {
  description = "Kubernetes API server host"
  type        = string
  default     = null
}

variable "kubernetes_token" {
  description = "Kubernetes authentication token"
  type        = string
  default     = null
  sensitive   = true
}

variable "kubernetes_ca_certificate" {
  description = "Kubernetes CA certificate"
  type        = string
  default     = null
  sensitive   = true
}

variable "vault_address" {
  description = "Vault server address"
  type        = string
  default     = "https://vault.helm-ai.com:8200"
}

variable "vault_token" {
  description = "Vault authentication token"
  type        = string
  default     = null
  sensitive   = true
}

variable "datadog_api_key" {
  description = "Datadog API key"
  type        = string
  default     = null
  sensitive   = true
}

variable "datadog_site" {
  description = "Datadog site"
  type        = string
  default     = "datadoghq.com"
}

# Security Variables
variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable centralized logging"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable encryption for all resources"
  type        = bool
  default     = true
}

# Cost Control Variables
variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "engineering"
}

variable "project_code" {
  description = "Project code for cost allocation"
  type        = string
  default     = "helm-ai"
}

variable "environment_code" {
  description = "Environment code for cost allocation"
  type        = string
  default     = "prod"
}

# Networking Variables
variable "enable_nat_gateway" {
  description = "Enable NAT gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints"
  type        = bool
  default     = false
}

variable "enable_dns_resolution" {
  description = "Enable DNS resolution"
  type        = bool
  default     = true
}

# Monitoring Variables
variable "enable_cloudwatch" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_xray" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable AWS CloudTrail logging"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty threat detection"
  type        = bool
  default     = true
}

variable "enable_config_rules" {
  description = "Enable AWS Config rules"
  type        = bool
  default     = true
}

# Backup Variables
variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "backup_schedule" {
  description = "Backup schedule in cron format"
  type        = string
  default     = "0 2 * * *"
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "Backup region for cross-region backup"
  type        = string
  default     = "us-west-2"
}

# Scaling Variables
variable "enable_auto_scaling" {
  description = "Enable auto scaling"
  type        = bool
  default     = true
}

variable "scale_up_cooldown" {
  description = "Auto scaling scale up cooldown in seconds"
  type        = number
  default     = 300
}

variable "scale_down_cooldown" {
  description = "Auto scaling scale down cooldown in seconds"
  type        = number
  default     = 300
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for auto scaling"
  type        = number
  default     = 70
}

variable "target_memory_utilization" {
  description = "Target memory utilization for auto scaling"
  type        = number
  default     = 80
}

# Security Variables
variable "enable_security_groups" {
  description = "Enable detailed security groups"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Enable AWS WAF"
  type        = bool
  default     = true
}

variable "enable_shield" {
  description = "Enable AWS Shield"
  type        = bool
  default     = true
}

variable "enable_certificate_manager" {
  description = "Enable AWS Certificate Manager"
  type        = bool
  default     = true
}

variable "domain_name" {
  description = "Domain name for SSL certificate"
  type        = string
  default     = "helm-ai.com"
}

# Compliance Variables
variable "enable_compliance_logging" {
  description = "Enable compliance logging"
  type        = bool
  default     = true
}

variable "enable_audit_logging" {
  description = "Enable audit logging"
  type        =  bool
  default     = true
}

variable "enable_access_logging" {
  description = "Enable access logging"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC flow logs"
  type        = bool
  default     = true
}

# Performance Variables
variable "enable_performance_insights" {
  description = "Enable performance insights"
  type        bool
  default     = true
}

variable "enable_rds_performance_insights" {
  description = "Enable RDS performance insights"
  type        = bool
  default     = true
}

variable "enable_elasticache_performance_insights" {
  description = "Enable ElastiCache performance insights"
  type        = bool
  default     = true
}

# Multi-Region Variables
variable "enable_multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = false
}

variable "secondary_region" {
  description = "Secondary AWS region"
  type        = string
  default     = "us-west-2"
}

variable "enable_cross_zone_load_balancing" {
  description = "Enable cross-zone load balancing"
  type        = bool
  default     = true
}

variable "enable_connection_draining" {
  description = "Enable connection draining"
  type        = bool
  default     = true
}

# Advanced Variables
variable "enable_service_mesh" {
  description = "Enable AWS App Mesh service mesh"
  type        = bool
  default     = false
}

variable "enable_fargate" {
  description = "Enable AWS Fargate"
  type        = bool
  default     = false
}

variable "enable_lambda" {
  description = "Enable AWS Lambda functions"
  type        = bool
  default     = false
}

variable "enable_step_functions" {
  description = "Enable AWS Step Functions"
  type        = bool
    default     = false
}

variable "enable_eventbridge" {
  description = "Enable AWS EventBridge"
  type        = bool
  default     = false
}

variable "enable_sqs" {
  description = "Enable AWS SQS"
  type        = bool
  default     = false
}

variable "enable_sns" {
  description = "Enable AWS SNS"
  type        = bool
  default     = false
}

variable "enable_dynamodb" {
  description = "Enable AWS DynamoDB"
  type        bool
  default     = false
}

# Custom Tags
variable "custom_tags" {
  description = "Custom tags for all resources"
  type        = map(string)
  default     = {}
}

variable "owner_tag" {
  description = "Owner tag for resources"
  type        = string
  default     = "devops"
}

variable "team_tag" {
  description = "Team tag for resources"
  type        string
  default     = "platform"
}

variable "environment_tag" {
  description = "Environment tag for resources"
  type        = string
  default     = var.environment
}

variable "application_tag" {
  description = "Application tag for resources"
  type        = string
  default     = "helm-ai"
}

variable "version_tag" {
  description = "Version tag for resources"
  type        string
  default     = "1.0.0"
}
