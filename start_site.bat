@echo off
title SignValid - CCA PDF Validator
echo ===================================================
echo Starting SignValid CCA PDF Validator & Public Tunnel
echo ===================================================

cd /d "%~dp0"

echo 1. Starting local FastAPI web server on port 8000...
start /b python -m uvicorn main:app --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak >nul

echo 2. Starting Cloudflare Public Tunnel...
start /b cloudflared.exe tunnel --url http://127.0.0.1:8000

echo.
echo Local Website:  http://127.0.0.1:8000
echo API Docs:       http://127.0.0.1:8000/docs
echo.
echo Check the cloudflared terminal output or task logs for your live public https:// URL.
echo Press any key to stop or close this window...
pause >nul
