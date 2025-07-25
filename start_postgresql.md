# 🐘 PostgreSQL Setup for Stock Scanner

## Quick Start PostgreSQL

### Windows (Git Bash)

1. **Install PostgreSQL**:
   - Download from: https://www.postgresql.org/download/windows/
   - Or use chocolatey: `choco install postgresql`

2. **Start PostgreSQL Service**:
   ```bash
   # Option 1: Windows Services
   net start postgresql-x64-13  # Adjust version number
   
   # Option 2: Command line
   pg_ctl -D "C:\Program Files\PostgreSQL\13\data" start
   
   # Option 3: Services GUI
   # Open services.msc and start "postgresql-x64-13"
   ```

3. **Create Database**:
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE stockscanner_db;
   
   # Exit
   \q
   ```

4. **Test Connection**:
   ```bash
   psql -U postgres -d stockscanner_db
   ```

## Alternative: Use SQLite (Easier)

If PostgreSQL is giving you trouble, switch to SQLite temporarily:

1. **Update .env file**:
   ```bash
   # Comment out PostgreSQL
   # DATABASE_URL=postgresql://postgres:StockScaner2010@localhost:5432/stockscanner_db
   
   # Use SQLite instead
   DATABASE_URL=sqlite:///db.sqlite3
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Current Status Check

Run this to check if PostgreSQL is running:
```bash
# Check if PostgreSQL is running
netstat -an | grep 5432

# Or try connecting
psql -U postgres -c "SELECT version();"
```