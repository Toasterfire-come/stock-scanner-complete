#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Stock Scanner MVP2 v3.4 Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} For the canonical setup guide, see docs/INSTALL.md"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}[1/8] Checking prerequisites...${NC}"
MISSING_DEPS=0

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    MISSING_DEPS=1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    MISSING_DEPS=1
fi

if ! command_exists yarn; then
    echo -e "${RED}❌ yarn is required but not installed.${NC}"
    MISSING_DEPS=1
fi

if ! command_exists docker; then
    echo -e "${YELLOW}⚠️  Docker is recommended but optional.${NC}"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Missing required dependencies. Please install them and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All required dependencies found${NC}"

# Setup backend
echo -e "\n${YELLOW}[2/8] Setting up backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${BLUE}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install Python dependencies
echo -e "${YELLOW}[3/8] Installing backend dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Generate SECRET_KEY
echo -e "\n${YELLOW}[4/8] Generating SECRET_KEY...${NC}"
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo -e "${GREEN}✅ SECRET_KEY generated${NC}"

# Create .env file
echo -e "\n${YELLOW}[5/8] Creating environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production.example .env
    # Replace SECRET_KEY in .env
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys (PayPal, Google OAuth, etc.)${NC}"
else
    echo -e "${BLUE}.env file already exists, skipping...${NC}"
fi

# Run migrations
echo -e "\n${YELLOW}[6/8] Setting up database...${NC}"
python manage.py migrate
echo -e "${GREEN}✅ Database migrations applied${NC}"

# Create superuser
echo -e "\n${YELLOW}[7/8] Creating admin user...${NC}"
echo -e "${BLUE}Please provide admin credentials:${NC}"
python manage.py createsuperuser

# Setup frontend
echo -e "\n${YELLOW}[8/8] Setting up frontend...${NC}"
cd ../frontend

# Install yarn dependencies
yarn install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Build frontend
yarn build
echo -e "${GREEN}✅ Frontend build complete${NC}"

# Final summary
cd ..
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Edit backend/.env with your API keys:"
echo "   - PAYPAL_CLIENT_ID and PAYPAL_SECRET"
echo "   - GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET"
echo "   - Database credentials if not using defaults"
echo ""
echo "2. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   yarn start"
echo ""
echo "4. Or use Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo -e "${YELLOW}Generated SECRET_KEY (saved to backend/.env):${NC}"
echo -e "${GREEN}$SECRET_KEY${NC}"
echo ""
echo -e "${BLUE}Access your application at:${NC}"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000/api/"
echo "   Admin Panel: http://localhost:8000/admin/"
echo "   Health Check: http://localhost:8000/api/health/"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
