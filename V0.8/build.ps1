# Script PowerShell pour compiler le client en executable
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Compilation du client en executable" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Installation des dependances..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Erreur lors de l'installation des dependances" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer"
    exit 1
}

Write-Host ""
Write-Host "[2/4] Installation de PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Erreur lors de l'installation de PyInstaller" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer"
    exit 1
}

Write-Host ""
Write-Host "[3/4] Nettoyage des anciens builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }

Write-Host ""
Write-Host "[4/4] Compilation avec PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean client.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Erreur lors de la compilation" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Compilation terminee avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "L'executable se trouve dans le dossier: dist\" -ForegroundColor White
Write-Host "Nom du fichier: Windows Driver Foundation Helper.exe" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur Entree pour ouvrir le dossier..."
Read-Host
Invoke-Item "dist"
