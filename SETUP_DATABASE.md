# Database Setup Guide

Simple step-by-step guide to set up your database for TradeScanPro.

## Option 1: MySQL (Recommended for Production)

### Step 1: Install MySQL
Download and install MySQL from https://dev.mysql.com/downloads/mysql/

### Step 2: Create Database
Open MySQL command line or workbench and run:
```sql
CREATE DATABASE tradescanpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tradescan_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON tradescanpro.* TO 'tradescan_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3: Configure Environment
Update your `.env` file:
```
DB_ENGINE=django.db.backends.mysql
DB_NAME=tradescanpro
DB_USER=tradescan_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
```

### Step 4: Run Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```

## Option 2: PostgreSQL (Alternative)

### Step 1: Install PostgreSQL
Download from https://www.postgresql.org/download/

### Step 2: Create Database
```sql
CREATE DATABASE tradescanpro;
CREATE USER tradescan_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE tradescanpro TO tradescan_user;
```

### Step 3: Configure Environment
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=tradescanpro
DB_USER=tradescan_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 4 & 5: Same as MySQL above

## Verify Setup

Run this command to verify database connection:
```bash
python manage.py dbshell
```

If successful, you'll see the database prompt.

## Populate Stock Data

Run the daily scanner to populate initial stock data:
```bash
python realtime_daily_yfinance.py
```

This will take 2-3 hours to complete initial population.

## Troubleshooting

**Connection Refused**: Check if MySQL/PostgreSQL service is running
**Access Denied**: Verify username and password in .env
**Unknown Database**: Ensure you created the database
