# Variables for Stock Scanner Pro AWS Infrastructure

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Name of the project (used for resource naming)"
  type        = string
  default     = "stock-scanner-pro"
}

# Networking Variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24"]
}

# EC2 Instance Variables
variable "web_instance_type" {
  description = "EC2 instance type for web servers"
  type        = string
  default     = "t3.medium"
}

variable "data_fetcher_instance_type" {
  description = "EC2 instance type for data fetcher server"
  type        = string
  default     = "t3.medium"
}

# Auto Scaling Group Variables
variable "asg_min_size" {
  description = "Minimum number of instances in Auto Scaling Group"
  type        = number
  default     = 4
}

variable "asg_max_size" {
  description = "Maximum number of instances in Auto Scaling Group"
  type        = number
  default     = 8
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in Auto Scaling Group"
  type        = number
  default     = 4
}

# Database Variables
variable "db_instance_type" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.large"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (GB)"
  type        = number
  default     = 1000
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "stockscanner"
}

variable "db_username" {
  description = "Username for database admin"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Password for database admin"
  type        = string
  sensitive   = true
  default     = "ChangeMe123!"
  
  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters long."
  }
}

# Cache Variables
variable "cache_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "cache_num_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 2
}

# Feature Flags
variable "enable_cloudfront" {
  description = "Enable CloudFront distribution"
  type        = bool
  default     = true
}

variable "enable_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

# Cost Optimization Variables
variable "enable_spot_instances" {
  description = "Use spot instances for cost optimization (non-production)"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 35
    error_message = "Backup retention must be between 1 and 35 days."
  }
}

# Monitoring Variables
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Security Variables
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access ALB"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_waf" {
  description = "Enable AWS WAF for additional security"
  type        = bool
  default     = true
}

# Scaling Variables
variable "cpu_scale_up_threshold" {
  description = "CPU utilization threshold for scaling up"
  type        = number
  default     = 70
}

variable "cpu_scale_down_threshold" {
  description = "CPU utilization threshold for scaling down"
  type        = number
  default     = 40
}

variable "scale_up_cooldown" {
  description = "Cooldown period after scaling up (seconds)"
  type        = number
  default     = 300
}

variable "scale_down_cooldown" {
  description = "Cooldown period after scaling down (seconds)"
  type        = number
  default     = 300
}

# Application Variables
variable "app_version" {
  description = "Application version for deployment"
  type        = string
  default     = "1.0.0"
}

variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate in ACM (optional)"
  type        = string
  default     = ""
}

# Notification Variables
variable "notification_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
  default     = ""
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

# Cost Control Variables
variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 1000
}

variable "cost_alert_thresholds" {
  description = "Cost alert thresholds as percentages of budget"
  type        = list(number)
  default     = [50, 80, 100]
}

# Data Fetcher Configuration
variable "stock_api_key" {
  description = "API key for stock data provider"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stock_api_endpoint" {
  description = "Endpoint for stock data API"
  type        = string
  default     = "https://api.example.com"
}

variable "data_fetch_interval" {
  description = "Interval for fetching stock data (in minutes)"
  type        = number
  default     = 5
}

# Backup Configuration
variable "s3_backup_bucket" {
  description = "S3 bucket name for backups (will be created if not exists)"
  type        = string
  default     = ""
}

variable "backup_schedule" {
  description = "Cron expression for backup schedule"
  type        = string
  default     = "0 2 * * *"  # Daily at 2 AM
}

# Performance Variables
variable "db_performance_insights_retention_period" {
  description = "Performance Insights retention period in days"
  type        = number
  default     = 7
}

variable "cache_ttl_seconds" {
  description = "Default cache TTL in seconds"
  type        = number
  default     = 300
}

# Disaster Recovery Variables
variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for disaster recovery"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "AWS region for cross-region backups"
  type        = string
  default     = "us-west-2"
}

# Development/Testing Variables
variable "create_bastion_host" {
  description = "Create bastion host for development access"
  type        = bool
  default     = false
}

variable "enable_ssh_access" {
  description = "Enable SSH access to instances"
  type        = bool
  default     = true
}

variable "ssh_key_name" {
  description = "Name of AWS key pair for SSH access"
  type        = string
  default     = ""
}

# Local tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Output Variables for Dependent Resources
variable "create_route53_zone" {
  description = "Create Route53 hosted zone for domain"
  type        = bool
  default     = false
}

variable "create_acm_certificate" {
  description = "Create ACM certificate for domain"
  type        = bool
  default     = false
}