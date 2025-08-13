# Outputs for Stock Scanner Pro Infrastructure

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

# Load Balancer Outputs
output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

# Application URL
output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

# Database Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database admin username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# Cache Outputs
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.main.port
}

# Auto Scaling Group Outputs
output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.web.name
}

output "autoscaling_group_arn" {
  description = "ARN of the Auto Scaling Group"
  value       = aws_autoscaling_group.web.arn
}

# Data Fetcher Outputs
output "data_fetcher_instance_id" {
  description = "Instance ID of the data fetcher server"
  value       = aws_instance.data_fetcher.id
}

output "data_fetcher_private_ip" {
  description = "Private IP of the data fetcher server"
  value       = aws_instance.data_fetcher.private_ip
}

# S3 Bucket Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

# CloudFront Outputs (if enabled)
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].id : null
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "web_security_group_id" {
  description = "ID of the web servers security group"
  value       = aws_security_group.web.id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "ID of the cache security group"
  value       = aws_security_group.cache.id
}

# Monitoring Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = "/aws/ec2/${var.project_name}"
}

# Cost and Resource Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost in USD"
  value = {
    base_configuration = "510"
    peak_configuration = "723"
    average_expected   = "600-650"
  }
}

output "resource_summary" {
  description = "Summary of created resources"
  value = {
    vpc_subnets       = length(aws_subnet.public) + length(aws_subnet.private) + length(aws_subnet.database)
    ec2_instances     = var.asg_desired_capacity + 1  # ASG instances + data fetcher
    rds_instances     = 1
    cache_nodes       = var.cache_num_nodes
    load_balancers    = 1
    s3_buckets        = 1
    cloudfront_distrs = var.enable_cloudfront ? 1 : 0
  }
}

# Connection Information
output "connection_info" {
  description = "Connection information for the deployed infrastructure"
  value = {
    web_url           = "http://${aws_lb.main.dns_name}"
    database_host     = aws_db_instance.main.endpoint
    redis_host        = aws_elasticache_replication_group.main.configuration_endpoint_address
    region            = var.aws_region
    environment       = var.environment
  }
  sensitive = true
}

# Deployment Information
output "deployment_info" {
  description = "Information about the deployment"
  value = {
    project_name      = var.project_name
    environment       = var.environment
    region            = var.aws_region
    vpc_id            = aws_vpc.main.id
    deployment_date   = timestamp()
    terraform_version = "~> 1.0"
  }
}

# DNS Information (for Route53 setup)
output "dns_setup_info" {
  description = "Information needed for DNS setup"
  value = {
    load_balancer_dns = aws_lb.main.dns_name
    load_balancer_zone_id = aws_lb.main.zone_id
    cloudfront_dns = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].domain_name : null
    cloudfront_zone_id = var.enable_cloudfront ? aws_cloudfront_distribution.main[0].hosted_zone_id : null
  }
}

# Backup Information
output "backup_info" {
  description = "Backup configuration information"
  value = {
    rds_backup_retention = aws_db_instance.main.backup_retention_period
    rds_backup_window   = aws_db_instance.main.backup_window
    s3_bucket_name      = aws_s3_bucket.main.id
    s3_versioning       = "Enabled"
  }
}

# Scaling Information
output "scaling_info" {
  description = "Auto scaling configuration"
  value = {
    min_capacity          = var.asg_min_size
    max_capacity          = var.asg_max_size
    desired_capacity      = var.asg_desired_capacity
    scale_up_threshold    = var.cpu_scale_up_threshold
    scale_down_threshold  = var.cpu_scale_down_threshold
    instance_type         = var.web_instance_type
    estimated_users_per_instance = "500-600"
    total_capacity_estimate = "${var.asg_min_size * 500}-${var.asg_max_size * 600}"
  }
}

# Quick Start Commands
output "quick_start_commands" {
  description = "Commands to get started with the deployment"
  value = {
    check_status = "aws elbv2 describe-target-health --target-group-arn ${aws_lb_target_group.web.arn}"
    view_logs    = "aws logs describe-log-groups --log-group-name-prefix '/aws/ec2/${var.project_name}'"
    scale_up     = "aws autoscaling set-desired-capacity --auto-scaling-group-name ${aws_autoscaling_group.web.name} --desired-capacity ${var.asg_max_size}"
    scale_down   = "aws autoscaling set-desired-capacity --auto-scaling-group-name ${aws_autoscaling_group.web.name} --desired-capacity ${var.asg_min_size}"
  }
}