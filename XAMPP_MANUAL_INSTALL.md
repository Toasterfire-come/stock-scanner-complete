# 🔧 XAMPP Manual Installation Guide

## The Problem
The automated XAMPP installation failed with "The system cannot execute the specified program." This is commonly caused by:

- **Antivirus blocking** the installer
- **Windows Defender** quarantining the file
- **Permissions issues** (not running as Administrator)
- **Corrupted download** (incomplete or damaged installer)
- **Missing dependencies** (Visual C++ redistributables)

## 🎯 QUICK SOLUTION (Recommended)

### Step 1: Manual Download
1. **Open your browser** and go to: https://www.apachefriends.org/download.html
2. **Download XAMPP for Windows** (PHP 8.2.x version)
3. **File should be**: `xampp-windows-x64-8.2.12-0-VS16-installer.exe` (or similar)
4. **File size**: Should be around 150-200 MB

### Step 2: Install XAMPP
1. **Right-click** the downloaded installer
2. **Select "Run as administrator"** (IMPORTANT!)
3. **Installation path**: Use default `C:\xampp`
4. **Components**: Select at minimum:
   - ✅ Apache
   - ✅ MySQL  
   - ✅ phpMyAdmin
   - ✅ PHP
5. **Firewall**: Allow access when Windows asks
6. **Services**: Choose to start services after installation

### Step 3: Verify Installation
1. **XAMPP Control Panel** should open automatically
2. **Start Services**:
   - Click **START** next to Apache (wait for green "Running")
   - Click **START** next to MySQL (wait for green "Running")
3. **Test**: Open browser and go to `http://localhost` (should show XAMPP dashboard)

### Step 4: Configure for Stock Scanner
```bash
# Once XAMPP is running, configure the database:
fix_xampp_mysql.bat

# Then set up Django:
python manage.py migrate
python manage.py runserver
```

## 🔍 Alternative: Use Our Debug Script

If you want to try the automated approach with better diagnostics:

```bash
# Run the enhanced installer with debugging:
xampp_installer_debug.bat
```

This script will:
- ✅ Test multiple download methods
- ✅ Verify file integrity
- ✅ Try different installation approaches  
- ✅ Check administrator privileges
- ✅ Provide detailed error messages
- ✅ Guide you through manual steps if needed

## 🚨 Common Issues & Solutions

### Issue 1: "The system cannot execute the specified program"
**Solutions:**
- Run as Administrator (right-click → Run as administrator)
- Temporarily disable antivirus
- Check Windows Defender quarantine
- Re-download the installer (may be corrupted)

### Issue 2: Antivirus Blocking Installation
**Solutions:**
- Add `C:\xampp` to antivirus exclusions
- Temporarily disable real-time protection
- Add the installer to trusted files
- Use Windows Defender exclusions

### Issue 3: Download Keeps Failing
**Solutions:**
- Use a different browser
- Disable browser extensions
- Clear browser cache
- Use direct download link: https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe

### Issue 4: Installation Hangs or Crashes
**Solutions:**
- Close all other programs
- Ensure 1GB+ free disk space
- Install Visual C++ Redistributable first
- Restart computer and try again

### Issue 5: Services Won't Start
**Solutions:**
- Check if ports 80 (Apache) and 3306 (MySQL) are free
- Disable IIS if installed (uses port 80)
- Stop other MySQL services
- Run XAMPP Control Panel as Administrator

## 🎯 What to Do After XAMPP is Installed

Once XAMPP is successfully installed and running:

### 1. Verify Services
- **Apache**: Should show green "Running" status
- **MySQL**: Should show green "Running" status  
- **Test**: Visit `http://localhost` and `http://localhost/phpmyadmin`

### 2. Configure Stock Scanner Database
```bash
# Run our configuration script:
fix_xampp_mysql.bat
```

This will:
- Create the `stockscanner` database
- Set up proper MySQL configurations
- Test the Django connection
- Create database tables

### 3. Start Django Development Server
```bash
# Set up Django:
python manage.py migrate
python manage.py runserver

# In another terminal, start the stock scheduler:
python start_stock_scheduler.py --background
```

### 4. Access Your Applications
- **Django Admin**: http://localhost:8000/admin/
- **Stock Scanner API**: http://localhost:8000/api/
- **WordPress Integration**: http://localhost:8000/api/wordpress/
- **phpMyAdmin**: http://localhost/phpmyadmin/

## 🔄 Complete Workflow

```bash
# 1. Install XAMPP manually (see steps above)
# 2. Configure for stock scanner:
fix_xampp_mysql.bat

# 3. Set up Django:
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 4. Start background stock updates:
python start_stock_scheduler.py --background

# 5. Test everything:
# - Visit http://localhost:8000/
# - Visit http://localhost:8000/api/stocks/
# - Visit http://localhost/phpmyadmin/
```

## 📞 Still Having Issues?

If manual installation still fails:

1. **Check System Requirements**:
   - Windows 10/11
   - 1GB+ free space
   - Administrative privileges

2. **Try Alternative Tools**:
   - **WAMP Server**: https://www.wampserver.com/
   - **MAMP**: https://www.mamp.info/en/windows/
   - **Local by Flywheel**: https://localwp.com/

3. **Use Cloud Alternative**:
   - Set up MySQL on a cloud service
   - Update Django settings to use remote database
   - Continue with local Python/Django development

The manual installation approach has a very high success rate and gives you full control over the process!