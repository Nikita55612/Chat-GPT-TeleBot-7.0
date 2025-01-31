@echo off
setlocal enabledelayedexpansion
title telebot
cd "%~dp0"

set _main_pyscript=main.py
set _requirements='pyTelegramBotAPI==4.16.0', '-U g4f', 'openai==1.12.0', 'tiktoken==0.6.0', 'matplotlib==3.8.3', 'pydantic==2.6.0', 'soundfile==0.12.1', 'SpeechRecognition==3.10.1', 'YooMoney==0.1.0'
set _pip_install_pyscript="import subprocess, sys; requirements = [%_requirements%]; freeze = subprocess.check_output(f'{sys.executable} -m pip freeze').decode().split(); [subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + r.split(' ')) for r in requirements if r not in freeze]"
set _python_version_install=3.11.6

python --version
if %errorlevel% neq 0 (
    for /f "tokens=1,2 delims=." %%a in ("%_python_version_install%") do (
        set X_vercion=%%a
        set Y_vercion=%%b
        )
    if not exist %LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion! (
        curl https://www.python.org/ftp/python/%_python_version_install%/python-%_python_version_install%-amd64.exe --output %USERPROFILE%\Downloads\python-%_python_version_install%-amd64.exe
        %USERPROFILE%\Downloads\python-%_python_version_install%-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 
        if not exist %LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion! (
            echo python failed to install! install python manually https://www.python.org/downloads/ or rerun the script as administrator.
            pause && exit 1
        ) else (set _python_dir=%LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion!\)
    ) else (
        setx /M path "%PATH%;%LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion!\"
        setx /M path "%PATH%;%LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion!\Scripts\"
        set _python_dir=%LocalAppData%\Programs\Python\Python!X_vercion!!Y_vercion!\
    )
    if not exist venv\ (!_python_dir!python.exe -m venv venv)
) else (
    if not exist venv\ (python -m venv venv)
)
call venv/Scripts/activate.bat
python -m pip install --upgrade pip
python -c %_pip_install_pyscript%
cls
python %_main_pyscript%
%SystemRoot%\System32\cmd.exe

