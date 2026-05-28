@echo off
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
    echo [Error] Execution environment not found! 
    echo Please run 'setup.bat' first to deploy the environment.
    pause
    exit /b
)
echo [Launching] Dataset Tagger and Translator...
venv\Scripts\python.exe dataset_tagger.py
pause