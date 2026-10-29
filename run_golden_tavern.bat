@echo off
cd /d "%~dp0"
set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

rem Reuse the working project environment if Cloudflare setup already created it.
if exist ".tmp\cloudflare-env\Scripts\python.exe" (
  set "GOLDEN_TAVERN_PYTHON=.tmp\cloudflare-env\Scripts\python.exe"
  goto run_app
)

rem Prefer the Python runtime bundled with Codex, like Daybook's launcher.
if exist "%CODEX_PYTHON%" (
  set "GOLDEN_TAVERN_PYTHON=%CODEX_PYTHON%"
  goto run_app
)

where py >nul 2>nul
if not errorlevel 1 (
  py -3 --version >nul 2>nul
  if not errorlevel 1 (
    set "GOLDEN_TAVERN_PYTHON=py -3"
    goto run_app
  )
)

where python >nul 2>nul
if not errorlevel 1 (
  python --version >nul 2>nul
  if not errorlevel 1 (
    set "GOLDEN_TAVERN_PYTHON=python"
    goto run_app
  )
)

echo Python 3 was not found. Install Python and try again.
pause
exit /b 1

:run_app
%GOLDEN_TAVERN_PYTHON% -c "import flask" >nul 2>nul
if errorlevel 1 (
  echo Preparing Golden Tavern the first time. This may take a minute...
  if not exist ".runtime" mkdir ".runtime"
  %GOLDEN_TAVERN_PYTHON% -m pip install --target .runtime -r requirements-local.txt
  if errorlevel 1 (
    echo Setup could not finish. Check your internet connection and try again.
    pause
    exit /b 1
  )
  set "PYTHONPATH=%CD%\.runtime"
)

%GOLDEN_TAVERN_PYTHON% -u app.py
if errorlevel 1 (
  echo Golden Tavern stopped with an error. Read the message above.
  pause
)
