@echo off
cd /d "%~dp0"
set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if not exist "%CODEX_PYTHON%" (
  echo The Python runtime bundled with Codex was not found.
  echo To build GoldenTavern.exe, install Python 3.10 or newer and update this script.
  pause
  exit /b 1
)

if not exist ".tmp" mkdir ".tmp"
if not exist ".builddeps" mkdir ".builddeps"
set "TEMP=%CD%\.tmp"
set "TMP=%CD%\.tmp"
set "PYINSTALLER_CONFIG_DIR=%CD%\.tmp\pyinstaller"

if not exist ".builddeps\PyInstaller\__init__.py" (
  echo Preparing the one-time packaging tools...
  "%CODEX_PYTHON%" -m pip install --target .builddeps -r requirements-build.txt
  if errorlevel 1 goto failed
)

set "PYTHONPATH=%CD%\.builddeps"
echo Building GoldenTavern.exe...
"%CODEX_PYTHON%" -m PyInstaller --clean --noconfirm --onefile --console --name GoldenTavern --workpath .build --distpath . --add-data "templates;templates" --add-data "static;static" app.py
if errorlevel 1 goto failed

echo.
echo Build complete: %CD%\GoldenTavern.exe
pause
exit /b 0

:failed
echo.
echo The build failed. Read the error above.
pause
exit /b 1
