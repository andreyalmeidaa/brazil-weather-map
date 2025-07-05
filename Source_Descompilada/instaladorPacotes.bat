@echo off
setlocal

echo Verificando se o Python esta instalado...

python --version >nul 2>&1
if errorlevel 1 (
    echo Python nao foi encontrado no sistema.
    echo Por favor, instale o Python antes de continuar.
    echo Voce pode baixar em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python encontrado!
echo Versao:
python --version

echo.
set /p continuar=Deseja continuar e instalar os pacotes Python? (S/N): 

if /I "%continuar%" neq "S" (
    echo Instalacao cancelada pelo usuario.
    pause
    exit /b 0
)

echo Instalando pacotes...

pip install requests
pip install unidecode
pip install PyQt5
pip install svg.path
pip install PyQtWebEngine
pip install feedparser

echo.
echo Instalacao concluida!
pause