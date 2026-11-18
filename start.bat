@echo off
title Cut it by Ai With Atif
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m studio.server
pause
