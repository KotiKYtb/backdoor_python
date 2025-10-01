@echo off
echo ========================================
echo    Compilation du client en executable
echo ========================================
echo.

echo [1/4] Installation des dependances...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Erreur lors de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo [2/4] Installation de PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo [!] Erreur lors de l'installation de PyInstaller
    pause
    exit /b 1
)

echo.
echo [3/4] Nettoyage des anciens builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo [4/4] Compilation avec PyInstaller...
pyinstaller --clean client.spec
if %errorlevel% neq 0 (
    echo [!] Erreur lors de la compilation
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Compilation terminee avec succes !
echo ========================================
echo.
echo L'executable se trouve dans le dossier: dist\
echo Nom du fichier: Windows Driver Foundation Helper.exe
echo.
echo Appuyez sur une touche pour ouvrir le dossier...
pause >nul
explorer dist
