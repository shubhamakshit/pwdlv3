@echo off
REM Batch script for running the Python script pwdl.py

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not found in the PATH.
    exit /b 1
)

REM Define paths to executables
set SCRIPT_DIR=%~dp0
set BIN_DIR=%SCRIPT_DIR%bin
set MP4DECRYPT=%BIN_DIR%\mp4decrypt.exe
@REM set VSD=%BIN_DIR%\vsd.exe

REM Check if bin directory exists, create if it doesn't
if not exist "%BIN_DIR%" (
    mkdir "%BIN_DIR%"
)

REM Check if mp4decrypt.exe exists
if not exist "%MP4DECRYPT%" (
    echo mp4decrypt.exe not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/shubhamakshit/pwdlv3_assets/raw/main/Windows/x86_64/mp4decrypt.exe' -OutFile '%MP4DECRYPT%'" >nul 2>&1
    if errorlevel 1 (
        echo Failed to download mp4decrypt.exe
    ) else (
        echo Successfully downloaded mp4decrypt.exe
    )
)

@REM REM Check if vsd.exe exists
@REM if not exist "%VSD%" (
@REM     echo vsd.exe not found. Downloading...
@REM     powershell -Command "Invoke-WebRequest -Uri 'https://github.com/shubhamakshit/pwdlv3_assets/raw/main/Windows/x86_64/vsd.exe' -OutFile '%VSD%'" >nul 2>&1
@REM     if errorlevel 1 (
@REM         echo Failed to download vsd.exe
@REM     ) else (
@REM         echo Successfully downloaded vsd.exe
@REM     )
@REM )

REM Run the Python script with the provided arguments
python "%~dp0pwdl.py" %*
