@echo off
echo ========================================
echo Diabetes Prediction App - Windows Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Create .env file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env >nul
    echo [OK] .env file created
    echo [WARNING] Edit .env file with your credentials!
) else (
    echo [WARNING] .env file already exists
)
echo.

REM Train ML model
echo Training machine learning model...
if exist diabetes_model.pkl (
    echo [WARNING] Model files exist. Skipping training...
) else (
    python train_model.py
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to train model
        pause
        exit /b 1
    )
    echo [OK] ML model trained successfully
)
echo.

REM Initialize database
echo Initializing database...
python -c "from app import init_db; init_db(); print('Database initialized')"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to initialize database
    pause
    exit /b 1
)
echo [OK] Database initialized
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file: notepad .env
echo 2. Start the app: python app.py
echo 3. Visit: http://127.0.0.1:8080
echo.
echo Default credentials:
echo   Admin: admin / admin123
echo   Doctor key: HEALTH2025
echo.
pause
