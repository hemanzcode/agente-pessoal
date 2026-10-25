@echo off
setlocal
title Mike - Agente Pessoal
cd /d "%~dp0"

set "MIKE_PYTHON=%~dp0.venv\Scripts\python.exe"
set "MIKE_APP=%~dp0app.py"

if not exist "%MIKE_APP%" (
    echo Erro: app.py nao foi encontrado nesta pasta.
    echo Extraia o projeto inteiro do arquivo ZIP antes de iniciar o Mike.
    pause
    exit /b 1
)

if not exist "%MIKE_PYTHON%" (
    echo Erro: o ambiente Python do Mike nao foi encontrado.
    echo Siga o README.md para instalar o Python e preparar o ambiente .venv.
    pause
    exit /b 1
)

"%MIKE_PYTHON%" "%MIKE_APP%" %*
set "MIKE_EXIT_CODE=%ERRORLEVEL%"

echo.
if "%MIKE_EXIT_CODE%"=="0" (
    echo O Mike foi encerrado.
) else (
    echo O Mike terminou com um erro. Consulte a mensagem acima.
)
pause
exit /b %MIKE_EXIT_CODE%
