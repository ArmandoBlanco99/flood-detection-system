@echo off
REM ============================================
REM Start the application with Cloudflare Tunnel
REM ============================================

echo.
echo 🌊 Sistema de Alertas de Inundaciones - CDMX
echo ============================================
echo.

REM Get the current directory
setlocal enabledelayedexpansion

echo [1/2] Iniciando servidor Flask...
echo.

REM Start Flask in the background
start "Flask Server" cmd /k "cd /d %~dp0..\src && python flask_server.py"

timeout /t 3 /nobreak

echo.
echo [2/2] Iniciando Cloudflare Tunnel...
echo.

REM Note: Assumes cloudflared is installed and available on PATH
REM Otherwise, replace cloudflared with its full path

cloudflared tunnel run sistema-inundaciones

echo.
echo ============================================
echo Para detener: Presiona Ctrl+C en ambas ventanas
echo ============================================
