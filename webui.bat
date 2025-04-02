@echo off
REM --------------------------
REM WebUI Setup Batch File
REM Critical Implementation
REM --------------------------

REM Capture root directory at launch
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

REM 1. Backend Environment Setup
echo === Backend Setup ===
pushd "%ROOT_DIR%\webui\backend"

REM 1.1 Check for Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    echo Install Python or add to PATH: https://docs.python.org/3/using/windows.html
    pause
    exit /b 1
)

REM 1.2 Create virtual environment if missing
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv "venv"
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM 1.3 Install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install flask flask-cors >nul
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM 2. VS Code Configuration
echo === VS Code Setup ===
echo To configure VS Code properly:
echo 1. Open the project folder in VS Code
echo 2. Press Ctrl+Shift+P -> "Python: Select Interpreter"
echo 3. Choose: .\webui\backend\venv\Scripts\python.exe
echo 4. Reload VS Code if needed

REM 3. Server Management
echo === Starting Servers ===
start "Backend" cmd /k "pushd "%ROOT_DIR%\webui\backend" && call venv\Scripts\activate.bat && python app.py"
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "pushd "%ROOT_DIR%\webui\frontend" && python -m http.server 8000"

REM 4. Browser Launch Section
echo === Browser Launch ===

REM Find Firefox executable
set "FIREFOX_PATH="
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    set "FIREFOX_PATH=%ProgramFiles%\Mozilla Firefox\firefox.exe"
)
if exist "%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe" (
    set "FIREFOX_PATH=%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
)

REM Launch URLs in Firefox if found
if defined FIREFOX_PATH (
    echo Launching Firefox...
    start "" "%FIREFOX_PATH%" "http://localhost:5000/api/data" "http://localhost:8000"
) else (
    echo Firefox not found in default locations!
    echo Using default browser instead...
    start "" http://localhost:5000/api/data
    start "" http://localhost:8000
)

REM 5. Delay and Exit
echo === Setup Complete ===
echo Press any key to exit...
pause >nul
exit /b