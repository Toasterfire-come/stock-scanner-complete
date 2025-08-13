# Stock Scanner Pro - AWS EC2 Deployment Guide

## Prerequisites

### 1. AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Terraform installed (version 1.0+)
- Domain name (optional, for custom domain)

### 2. Required AWS Permissions
Your AWS user/role needs the following permissions:
- EC2 (full access)
- RDS (full access)
- ElastiCache (full access)
- VPC (full access)
- IAM (limited access for roles)
- S3 (full access)
- CloudWatch (full access)
- Auto Scaling (full access)
- Elastic Load Balancing (full access)
- CloudFront (optional)

## Quick Start Deployment

### Step 1: Clone Repository and Switch to EC2 Branch
```bash
git clone <your-repository>
cd <repository-name>
git checkout EC2
```

### Step 2: Configure Terraform Variables
Create a `terraform.tfvars` file:
```hcl
# Basic Configuration
project_name = "stock-scanner-pro"
environment  = "production"
aws_region   = "us-east-1"

# Database Configuration
db_password = "YourSecurePassword123!"
db_instance_type = "db.t3.large"

# Auto Scaling Configuration
asg_min_size = 4
asg_max_size = 8
asg_desired_capacity = 4

# Instance Types
web_instance_type = "t3.medium"
data_fetcher_instance_type = "t3.medium"

# Features
enable_cloudfront = true
enable_multi_az = true

# Monitoring
notification_email = "admin@yourdomain.com"

# Optional: Custom Domain
domain_name = "yourdomain.com"
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
```

### Step 3: Initialize and Deploy Infrastructure
```bash
cd terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
```

### Step 4: Configure DNS (if using custom domain)
After deployment, configure your DNS:
1. Get the Load Balancer DNS name from Terraform outputs
2. Create a CNAME record pointing your domain to the ALB DNS name
3. If using CloudFront, point to the CloudFront distribution instead

### Step 5: Upload WordPress Theme
1. SSH into one of the web servers (use bastion host if created)
2. Upload your Stock Scanner Pro theme to `/var/www/html/wp-content/themes/`
3. Activate the theme through WordPress admin

## Detailed Configuration

### Cost Optimization

#### Reserved Instances
For production workloads, consider purchasing Reserved Instances:
```bash
# Example: Purchase Reserved Instances for base capacity
aws ec2 purchase-reserved-instances-offering \
    --reserved-instances-offering-id <offering-id> \
    --instance-count 4
```

#### Spot Instances (Development)
For development environments, enable spot instances:
```hcl
# In terraform.tfvars
enable_spot_instances = true
```

### Security Configuration

#### Update Default Passwords
**IMPORTANT**: Change default passwords immediately after deployment:

1. **Database Password**
   ```bash
   # Connect to RDS instance
   psql -h <rds-endpoint> -U admin -d stockscanner
   
   # Change password
   ALTER USER admin WITH PASSWORD 'YourNewSecurePassword';
   ```

2. **WordPress Admin Password**
   ```bash
   # SSH to web server
   cd /var/www/html
   wp user update admin --user_pass=YourNewSecurePassword
   ```

#### Configure WAF (Optional)
```bash
# Create WAF Web ACL
aws wafv2 create-web-acl \
    --name stock-scanner-waf \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules file://waf-rules.json
```

### Monitoring Setup

#### CloudWatch Dashboards
Create custom dashboards for monitoring:
```bash
aws cloudwatch put-dashboard \
    --dashboard-name StockScannerPro \
    --dashboard-body file://dashboard.json
```

#### Alerts Configuration
Set up CloudWatch alarms:
```bash
# High CPU Alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "StockScanner-HighCPU" \
    --alarm-description "Alarm when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

### Backup Configuration

#### Automated Database Backups
RDS automatically backs up your database. To create manual snapshots:
```bash
aws rds create-db-snapshot \
    --db-instance-identifier stock-scanner-pro-db \
    --db-snapshot-identifier manual-snapshot-$(date +%Y%m%d)
```

#### Application Backups
The data fetcher automatically backs up to S3. To manually trigger:
```bash
# SSH to data fetcher instance
sudo systemctl start backup-service
```

## Scaling Operations

### Manual Scaling
```bash
# Scale up during high traffic
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name stock-scanner-pro-web-asg \
    --desired-capacity 8

# Scale down during low traffic
aws autoscaling set-desired-capacity \
    --auto-scaling-group-name stock-scanner-pro-web-asg \
    --desired-capacity 4
```

### Scheduled Scaling
```bash
# Scale up before market open (9 AM EST)
aws autoscaling put-scheduled-action \
    --auto-scaling-group-name stock-scanner-pro-web-asg \
    --scheduled-action-name scale-up-market-open \
    --recurrence "0 9 * * MON-FRI" \
    --desired-capacity 6

# Scale down after market close (4 PM EST)
aws autoscaling put-scheduled-action \
    --auto-scaling-group-name stock-scanner-pro-web-asg \
    --scheduled-action-name scale-down-market-close \
    --recurrence "0 16 * * MON-FRI" \
    --desired-capacity 4
```

## Maintenance Operations

### WordPress Updates
```bash
# SSH to web server
cd /var/www/html

# Update WordPress core
wp core update

# Update plugins
wp plugin update --all

# Update themes
wp theme update --all
```

### System Updates
```bash
# Updates are automatic, but to manually update:
sudo yum update -y
sudo systemctl restart httpd
```

### Database Maintenance
```bash
# Connect to database
psql -h <rds-endpoint> -U admin -d stockscanner

# Analyze tables
ANALYZE;

# Vacuum tables
VACUUM;

# Check database size
SELECT pg_size_pretty(pg_database_size('stockscanner'));
```

## Troubleshooting

### Common Issues

#### 1. High Memory Usage
```bash
# Check memory usage on web servers
free -m

# Restart Apache if needed
sudo systemctl restart httpd

# Check for memory leaks
sudo ps aux --sort=-%mem | head
```

#### 2. Database Connection Issues
```bash
# Check database status
aws rds describe-db-instances --db-instance-identifier stock-scanner-pro-db

# Check security groups
aws ec2 describe-security-groups --group-ids <db-security-group-id>

# Test connection from web server
telnet <rds-endpoint> 5432
```

#### 3. Load Balancer Health Checks Failing
```bash
# Check target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>

# Check health endpoint
curl http://<instance-ip>/health

# Check Apache status
sudo systemctl status httpd
```

#### 4. Cache Issues
```bash
# Connect to Redis
redis-cli -h <cache-endpoint>

# Check Redis status
INFO

# Clear cache if needed
FLUSHALL
```

### Log Locations
- **Web Server Logs**: `/var/log/httpd/`
- **WordPress Logs**: `/var/www/html/wp-content/debug.log`
- **Data Fetcher Logs**: `/var/log/stock-data-fetcher.log`
- **System Logs**: `/var/log/messages`
- **CloudWatch Logs**: Available in AWS Console

### Performance Monitoring
```bash
# Check system performance
top
htop
iostat

# Check disk usage
df -h

# Check network connections
netstat -an

# Check Apache performance
sudo apachectl status
```

## Disaster Recovery

### RDS Failover (Multi-AZ)
```bash
# Force failover for testing
aws rds reboot-db-instance \
    --db-instance-identifier stock-scanner-pro-db \
    --force-failover
```

### Application Recovery
```bash
# Restore from backup
aws s3 cp s3://your-backup-bucket/latest-backup.tar.gz /tmp/
cd /var/www/html
sudo tar -xzf /tmp/latest-backup.tar.gz
```

### Data Recovery
```bash
# Restore database from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier stock-scanner-pro-db-restored \
    --db-snapshot-identifier <snapshot-id>
```

## Cost Optimization Tips

### 1. Use Reserved Instances
- Purchase 1-year Reserved Instances for base capacity
- Can save 30-60% on compute costs

### 2. Optimize Instance Types
- Monitor CPU and memory usage
- Right-size instances based on actual usage
- Consider newer generation instances (t3 vs t2)

### 3. Use Spot Instances for Non-Critical Workloads
- Data processing jobs
- Development environments
- Background tasks

### 4. Implement Auto Scaling
- Scale down during off-hours
- Use scheduled scaling for predictable traffic patterns

### 5. Optimize Storage
- Use GP3 instead of GP2 for better performance/cost
- Implement lifecycle policies for S3 backups
- Clean up old snapshots and logs

## Security Best Practices

### 1. Network Security
- Use VPC with private subnets
- Implement security groups with least privilege
- Enable VPC Flow Logs

### 2. Access Control
- Use IAM roles instead of access keys
- Implement MFA for admin access
- Regular access review

### 3. Data Protection
- Enable encryption at rest and in transit
- Regular security patches
- Backup encryption

### 4. Monitoring
- Enable AWS CloudTrail
- Set up security alerts
- Regular security audits

## Support and Maintenance

### Regular Tasks
- **Daily**: Monitor dashboards and alerts
- **Weekly**: Review logs and performance metrics
- **Monthly**: Security updates and patches
- **Quarterly**: Cost optimization review
- **Annually**: Disaster recovery testing

### Contact Information
- AWS Support (if applicable)
- Internal team contacts
- Emergency procedures

## Conclusion

This infrastructure provides a robust, scalable foundation for Stock Scanner Pro that can handle 2000+ concurrent users with automatic scaling, high availability, and comprehensive monitoring. Regular maintenance and monitoring will ensure optimal performance and cost efficiency.

For additional support or questions about the deployment, refer to the AWS documentation or contact your infrastructure team.