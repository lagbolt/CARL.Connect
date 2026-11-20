@echo off
setlocal EnableDelayedExpansion

:: 1. Call PowerShell to output the exact timestamp format
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"`) do set TIMESTAMP=%%I

:: 2. Construct the directory name
set DIRNAME=%~dp0run_%TIMESTAMP%

:: 3. Create and enter the run directory
echo Creating directory: %DIRNAME%
mkdir %DIRNAME%

:: 4. Collect new catalog records
echo Collecting records ...
py %~dp0scan-current.py -o %DIRNAME%\new-records.mrc
echo Record collection done ...

:: 5. Set up checktools directory
set TOOLSDIR=%~dp0..\check_tools
echo linking to %TOOLSDIR%

:: 6. Run tools
py "%TOOLSDIR%\check-language.py" -i %DIRNAME%\new-records.mrc -o %DIRNAME%\check-language-report.txt -b
py "%TOOLSDIR%\check-names.py" -i %DIRNAME%\new-records.mrc -o %DIRNAME%\check-names-report.txt
py "%TOOLSDIR%\check-records.py" -i %DIRNAME%\new-records.mrc -o %DIRNAME%\check-records-report.txt -b
py "%TOOLSDIR%\check-subjects.py" -i %DIRNAME%\new-records.mrc -o %DIRNAME%\check-subjects-report.txt
echo Starting series check ...
py "%TOOLSDIR%\check-series.py" -i %DIRNAME%\new-records.mrc -o %DIRNAME%\check-series-report.csv
echo Done!