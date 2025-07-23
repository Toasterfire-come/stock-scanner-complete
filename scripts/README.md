# 🔧 Scripts Directory

This directory contains essential setup and utility scripts for the Stock Scanner platform.

## 📁 Directory Structure

```
scripts/
├── 📁 setup/          # Installation and setup scripts
│   ├── 📄 fix_migration_conflicts.py     # 🔧 Django migration conflict resolver
│   ├── 📄 windows_fix_install.py         # 🪟 Windows compatibility fixes
│   ├── 📄 install_missing_packages.py    # 📦 Package installation helper
│   ├── 📄 apply_yfinance_migrations.py   # 📊 Yahoo Finance integration setup
│   ├── 📄 run_migrations.py              # 🗄️ Database migration runner
│   └── 📄 setup_redis_windows.py         # 🔴 Redis Windows configuration
├── 📁 testing/        # Testing and validation scripts
│   ├── 📄 test_django_startup.py         # 🌐 Django application startup test
│   ├── 📄 test_yfinance_system.py        # 📈 Yahoo Finance API integration test
│   └── 📄 validate_migrations.py         # 🔍 Migration sequence validator
└── 📁 utils/         # Utility and maintenance scripts
    ├── 📄 enable_celery_beat.py          # 🔄 Celery task scheduler setup
    ├── 📄 fix_env_urls.py                # 🔧 Environment URL configuration
    └── 📄 check_syntax.py               # ✅ Code syntax validation
```

## 🚀 Essential Scripts

### Setup Scripts

#### Migration Conflict Resolver
```bash
# Fix Django migration conflicts (essential for setup)
python scripts/setup/fix_migration_conflicts.py
```

#### Windows Setup
```bash
# Windows compatibility fixes
python scripts/setup/windows_fix_install.py
```

#### Database Setup
```bash
# Run Django migrations
python scripts/setup/run_migrations.py
```

### Utility Scripts

#### Celery Setup
```bash
# Enable background task processing
python scripts/utils/enable_celery_beat.py
```

#### Environment Configuration
```bash
# Fix environment URLs and settings
python scripts/utils/fix_env_urls.py
```

### Testing Scripts

#### Django Startup Test
```bash
# Test Django application startup and configuration
python scripts/testing/test_django_startup.py
```

#### YFinance Integration Test
```bash
# Test Yahoo Finance API integration
python scripts/testing/test_yfinance_system.py
```

#### Migration Validation
```bash
# Validate Django migration sequence and dependencies
python scripts/testing/validate_migrations.py
```

## 📚 Documentation

- **[Django Migration Guide](../docs/DJANGO_MIGRATION_GUIDE.md)** - Migration troubleshooting
- **[Windows Production Guide](../docs/WINDOWS_PRODUCTION_DEPLOYMENT_GUIDE.md)** - Complete Windows setup
- **[Integration Summary](../docs/INTEGRATION_SUMMARY.md)** - Platform integration overview

## 🔧 Usage Examples

### Development Setup
```bash
# 1. Fix any migration conflicts
python scripts/setup/fix_migration_conflicts.py

# 2. Install missing packages
python scripts/setup/install_missing_packages.py

# 3. Run migrations
python scripts/setup/run_migrations.py

# 4. Enable Celery (optional)
python scripts/utils/enable_celery_beat.py
```

### Production Setup
```bash
# 1. Windows compatibility (if on Windows)
python scripts/setup/windows_fix_install.py

# 2. Fix migration conflicts
python scripts/setup/fix_migration_conflicts.py

# 3. Setup Redis (Windows)
python scripts/setup/setup_redis_windows.py

# 4. Apply migrations
python scripts/setup/run_migrations.py
```

## ⚠️ Important Notes

- **Always backup your database** before running migration scripts
- **Run scripts from the project root directory**
- **Activate your virtual environment** before running scripts
- **Check script output** for any errors or warnings

## 🆘 Troubleshooting

If you encounter issues:

1. **Check Python version**: Ensure Python 3.9+ is installed
2. **Verify virtual environment**: Make sure it's activated
3. **Check dependencies**: Run `pip install -r requirements.txt`
4. **Review logs**: Check script output for specific errors
5. **Consult documentation**: See the docs/ directory for guides