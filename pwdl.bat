@echo off
REM Batch script for running the Python script pwdl.py

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not found in the PATH.
    exit /b 1
)

REM Run the Python script with the provided arguments
python "%~dp0pwdl.py" %*
