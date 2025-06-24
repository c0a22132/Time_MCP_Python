@echo off
REM Time MCP Server Setup Script for Windows

echo Setting up Time MCP Server (Python)...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not installed. Please install Python 3.8 or later.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -e .

echo Setup complete!
echo.
echo To run the server:
echo   MCP Server: python -m time_mcp_server
echo   HTTP Server: python -m time_mcp_server --http
echo   Standalone: python -m time_mcp_server --standalone
echo.
echo To run tests:
echo   pip install pytest
echo   pytest

pause
