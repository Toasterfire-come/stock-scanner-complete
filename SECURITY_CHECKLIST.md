# Security Checklist for Stock Scanner Production

## Before Deployment:

### 1. Environment Variables
- [ ] Generate a new SECRET_KEY (minimum 50 characters)
- [ ] Set DEBUG=false
- [ ] Configure ALLOWED_HOSTS with your actual domain
- [ ] Use strong database passwords (minimum 16 characters)
- [ ] Use secure email passwords (app-specific passwords)

### 2. Database Security
- [ ] Create dedicated database user with minimal privileges
- [ ] Use strong passwords for all database accounts
- [ ] Enable SSL/TLS for database connections
- [ ] Regularly backup database with encryption

### 3. Web Server Security
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Configure HSTS headers
- [ ] Set secure cookie flags
- [ ] Configure CSP headers
- [ ] Hide server version information

### 4. Application Security
- [ ] Review all user input validation
- [ ] Enable CSRF protection
- [ ] Configure rate limiting
- [ ] Set up proper logging and monitoring
- [ ] Regular security updates

### 5. Infrastructure Security
- [ ] Keep operating system updated
- [ ] Configure firewall rules
- [ ] Use fail2ban or similar intrusion prevention
- [ ] Regular security audits
- [ ] Backup and disaster recovery plan

## Monitoring:
- [ ] Set up error monitoring (Sentry recommended)
- [ ] Configure log monitoring
- [ ] Set up uptime monitoring
- [ ] Regular performance monitoring
- [ ] Security scanning tools

## Compliance:
- [ ] GDPR compliance (if applicable)
- [ ] Data retention policies
- [ ] User privacy policies
- [ ] Terms of service
- [ ] Payment compliance (PCI DSS for Stripe)
