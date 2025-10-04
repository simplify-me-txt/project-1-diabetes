#!/bin/bash

echo "🏥 Diabetes Prediction App - Automated Setup"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env file with your credentials before running the app${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists. Skipping...${NC}"
fi

# Train ML model
echo ""
echo "Training machine learning model..."
if [ -f "diabetes_model.pkl" ] && [ -f "scaler.pkl" ]; then
    echo -e "${YELLOW}⚠ Model files already exist. Skipping training...${NC}"
    echo "  Delete diabetes_model.pkl and scaler.pkl to retrain"
else
    python3 train_model.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ML model trained successfully${NC}"
    else
        echo -e "${RED}❌ Failed to train model${NC}"
        exit 1
    fi
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from app import init_db; init_db(); print('Database initialized')"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
else
    echo -e "${RED}❌ Failed to initialize database${NC}"
    exit 1
fi

# Setup complete
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "3. Open your browser and visit:"
echo "   http://127.0.0.1:8080"
echo ""
echo "Default accounts:"
echo "  Admin: admin / admin123 (change in .env)"
echo "  Doctor secret key: HEALTH2025 (change in .env)"
echo ""
echo -e "${YELLOW}⚠ Remember to change default passwords before production!${NC}"
echo ""
