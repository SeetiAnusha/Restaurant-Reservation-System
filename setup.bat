@echo off
REM Restaurant Reservation Agent - Setup Script (Windows)

echo 🍽️  GoodFoods Reservation Agent Setup
echo ======================================
echo.

REM Check Python version
echo 📋 Checking Python version...
python --version

REM Create virtual environment
echo.
echo 🔧 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Virtual environment created
echo.
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your GROQ_API_KEY
) else (
    echo.
    echo ✅ .env file already exists
)

REM Generate restaurant data
echo.
echo 🎲 Generating restaurant data...
python data/generator.py

echo.
echo ======================================
echo ✨ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your GROQ_API_KEY
echo 2. Run: streamlit run frontend/streamlit_app.py
echo.
echo For testing: python evaluation/test_scenarios.py
echo ======================================
pause
