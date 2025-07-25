# Stock Scanner - Windows Setup Guide

This guide will help you set up the Stock Scanner application on Windows with MySQL database.

## 🚀 Quick Setup (Recommended)

### Prerequisites
1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **MySQL Server** - Download from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
3. **Git** (optional) - Download from [git-scm.com](https://git-scm.com)

### One-Click Setup
1. **Download/Clone the repository**
   ```bash
   git clone https://github.com/Toasterfire-come/stock-scanner-complete.git
   cd stock-scanner-complete
   ```

2. **Run the automated setup**
   - Double-click `windows_setup.bat` 
   - OR run in Command Prompt: `windows_setup.bat`
   - OR run the Python script directly: `python windows_mysql_setup.py`

3. **Follow the prompts**
   - Enter your MySQL root password when asked
   - Choose whether to create a Django admin user
   - Wait for the setup to complete

4. **Start the application**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Open your browser to: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🛠️ Manual Setup (Advanced Users)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements_windows.txt
```

### Step 2: Set up MySQL Database
1. **Start MySQL Server**
2. **Create database and user**:
   ```sql
   CREATE DATABASE stock_scanner_nasdaq;
   CREATE USER 'stock_scanner'@'localhost' IDENTIFIED BY 'StockScanner2024';
   GRANT ALL PRIVILEGES ON stock_scanner_nasdaq.* TO 'stock_scanner'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Step 3: Configure Environment
Create a `.env` file in the project root:
```env
DATABASE_URL=mysql://stock_scanner:StockScanner2024@localhost:3306/stock_scanner_nasdaq
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 6: Start the Server
```bash
python manage.py runserver
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Unicode Encoding Errors
**Error**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution**: Use the Windows-compatible scripts:
- Use `python windows_mysql_setup.py` instead of `python fix_migration_issue.py`
- All Unicode emojis have been replaced with plain text

#### 2. MySQL Connection Issues
**Error**: `Can't connect to MySQL server`

**Solutions**:
- Ensure MySQL Server is running
- Check if MySQL service is started in Windows Services
- Verify MySQL credentials in `.env` file
- Try connecting with MySQL Workbench first

#### 3. PyMySQL Installation Issues
**Error**: `No module named 'MySQLdb'`

**Solution**:
```bash
pip install PyMySQL
```
The `manage.py` file is already configured to use PyMySQL automatically.

#### 4. Migration Conflicts
**Error**: Migration conflicts or database schema issues

**Solution**:
```bash
python fix_migration_issue_windows.py
```

#### 5. Port Already in Use
**Error**: `That port is already in use`

**Solution**:
```bash
python manage.py runserver 8001
```
Or use any other available port.

## 📁 Project Structure

```
stock-scanner-complete/
├── manage.py                    # Django management script (MySQL configured)
├── windows_setup.bat           # Windows batch setup script
├── windows_mysql_setup.py      # Automated Python setup script
├── fix_migration_issue_windows.py  # Windows-compatible migration fixer
├── requirements_windows.txt    # Windows-specific requirements
├── .env                        # Environment configuration (created by setup)
├── stockscanner_django/        # Django project settings
├── stocks/                     # Main application
├── core/                       # Core functionality
└── data/                       # Data files
```

## 🔐 Security Notes

1. **Change the default SECRET_KEY** in production
2. **Use strong passwords** for MySQL users
3. **Don't commit `.env` file** to version control
4. **Enable HTTPS** in production environments

## 📊 Features

- **NASDAQ Stock Scanning**: Focus on NASDAQ-listed securities
- **Real-time Data**: Integration with Yahoo Finance
- **Advanced Filtering**: Multiple criteria for stock selection
- **Portfolio Analytics**: Track and analyze stock performance
- **REST API**: Full API access to stock data
- **Admin Interface**: Django admin for data management
- **Responsive Design**: Works on desktop and mobile

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the console
2. **Verify MySQL**: Ensure MySQL is running and accessible
3. **Check Python version**: Ensure you're using Python 3.8+
4. **Review .env file**: Verify database connection string
5. **Run diagnostics**: Use `python windows_mysql_setup.py` to re-run setup

## 🔄 Updates

To update the application:
```bash
git pull origin complete-stock-scanner-v1
python windows_mysql_setup.py  # Re-run setup if needed
python manage.py migrate        # Apply any new migrations
```

## 📝 Development

For development:
1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements_windows.txt
   ```

3. Run in debug mode (already enabled in `.env`)

## 🎯 Next Steps

After successful setup:
1. **Load stock data**: Use the management commands to populate the database
2. **Configure APIs**: Add your API keys to `.env` for real-time data
3. **Customize settings**: Modify Django settings as needed
4. **Set up production**: Configure for production deployment when ready

---

**Need help?** Check the main README.md or create an issue on GitHub.