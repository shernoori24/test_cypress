@echo off
echo ================================
echo CREATION NOUVELLE VERSION
echo ================================
echo.
echo Ce script va :
echo - Reconstruire l'executable
echo - Creer une nouvelle version dans le dossier versions/
echo.
pause
echo.
echo Construction en cours...
"%~dp0venv\Scripts\python.exe" update_app.py
echo.
echo ================================
echo VERSION CREEE AVEC SUCCES !
echo ================================
echo.
echo La nouvelle version est disponible dans le dossier versions/ !
echo Vous pouvez la distribuer directement depuis ce dossier.
echo.
pause
