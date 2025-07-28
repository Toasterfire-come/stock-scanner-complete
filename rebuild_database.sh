#!/bin/bash

# Exit on error
set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    set -a
    source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env)
    set +a
fi

# Set defaults if not set
DB_NAME=${DB_NAME:-stockscanner}
DB_USER=${DB_USER:-stockscanner}
DB_PASS=${DB_PASS:-StockScaner2010}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}

# Prompt for MySQL root password
read -sp "Enter MySQL root password: " MYSQL_ROOT_PASS

echo

# Drop and recreate the database
mysql -u root -p"$MYSQL_ROOT_PASS" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL ON $DB_NAME.* TO '$DB_USER'@'%' IDENTIFIED BY '$DB_PASS'; FLUSH PRIVILEGES;"
echo "[INFO] Database $DB_NAME dropped and recreated."

# Run Django migrations
python manage.py migrate

echo "[INFO] Migrations complete."

# Create default superuser (admin/admin123)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
echo "[INFO] Superuser 'admin' created with password 'admin123'."

# Load NASDAQ tickers
echo "[INFO] Loading NASDAQ tickers..."
python manage.py load_nasdaq_tickers --update-existing

echo "[INFO] Cleaning up bad data..."
python tools/fix_empty_ticker_rows.py

echo "[INFO] Database rebuild and data load complete!"

# Print summary
python -c "from stocks.models import Stock; print(f'Total stocks in DB: {Stock.objects.count()}')" | python manage.py shell