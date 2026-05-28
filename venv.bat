@echo off
cd /d "%~dp0"

echo [1/3] Creating virtual environment...
python -m venv venv

echo [2/3] Updating pip and installing dependencies...
:: Force update pip and specify the installation path
call venv\Scripts\python.exe -m ensurepip
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\python.exe -m pip install Pillow deep-translator

echo [3/3] Verifying installation...
:: Check if PIL (Pillow) is installed successfully
call venv\Scripts\python.exe -c "from PIL import Image; print('Pillow installed successfully!')"

echo.
echo ===========================================
echo Setup finished. If no error appeared above, 
echo you can run 'run.bat' to start the application.
echo ===========================================
pause