@echo off
REM Stellar Logic AI - Safe Rename Scripts
REM DO NOT EXECUTE WITHOUT BACKUP

echo ========================================
echo STELLAR LOGIC AI - SAFE RENAME SCRIPTS
echo ========================================
echo.
echo WARNING: This will rename helm-ai to stellar-logic-ai
echo Make sure you have a complete backup!
echo.
pause

REM Create backup folder with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "MIN=%dt:~10,2%"
set "SEC=%dt:~12,2%"

set "BACKUP_FOLDER=helm-ai-backup-%YYYY%%MM%%DD%-%HH%%MIN%%SEC%"

echo Creating backup in: %BACKUP_FOLDER%
xcopy "C:\Users\merce\Documents\helm-ai" "C:\Users\merce\Documents\%BACKUP_FOLDER%" /E /I /H /Y

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Backup failed!
    pause
    exit /b 1
)

echo Backup completed successfully!
echo.

REM Step 1: Update absolute paths in configuration files
echo Step 1: Updating absolute paths...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.md','*.py','*.yml','*.yaml','*.json','*.conf' | ForEach-Object { (Get-Content $_.FullName) -replace 'C:\\Users\\merce\\Documents\\helm-ai', 'C:\\Users\\merce\\Documents\\stellar-logic-ai' | Set-Content $_.FullName }"

REM Step 2: Update email domains
echo Step 2: Updating email domains...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.py','*.md','*.html','*.txt' | ForEach-Object { (Get-Content $_.FullName) -replace '@helm-ai\.com', '@stellar-logic.ai' | Set-Content $_.FullName }"

REM Step 3: Update logo references
echo Step 3: Updating logo references...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.html','*.md','*.css' | ForEach-Object { (Get-Content $_.FullName) -replace 'helm-ai-logo\.png', 'stellar-logic-ai-logo.png' | Set-Content $_.FullName }"

REM Step 4: Update URL references
echo Step 4: Updating URL references...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.py','*.md','*.yml','*.yaml','*.json' | ForEach-Object { (Get-Content $_.FullName) -replace 'https://.*\.helm-ai\.com', 'https://stellar-logic.ai' | Set-Content $_.FullName }"

REM Step 5: Update Unix paths
echo Step 5: Updating Unix paths...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.py','*.yml','*.yaml','*.conf' | ForEach-Object { (Get-Content $_.FullName) -replace '/var/lib/helm-ai', '/var/lib/stellar-logic-ai' | Set-Content $_.FullName }"

REM Step 6: Update storage paths
echo Step 6: Updating storage paths...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.py','*.yml','*.yaml' | ForEach-Object { (Get-Content $_.FullName) -replace 's3://helm-ai-backups', 's3://stellar-logic-ai-backups' | Set-Content $_.FullName }"

REM Step 7: Update user agent strings
echo Step 7: Updating user agent strings...
powershell -Command "Get-ChildItem -Path '.' -Recurse -Include '*.py' | ForEach-Object { (Get-Content $_.FullName) -replace 'Helm-AI-Webhook', 'Stellar-Logic-AI-Webhook' | Set-Content $_.FullName }"

echo.
echo All file updates completed!
echo.

REM Step 8: Rename the folder
echo Step 8: Renaming folder...
cd "C:\Users\merce\Documents"
ren "helm-ai" "stellar-logic-ai"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Folder rename failed!
    echo You may need to close any programs using the folder.
    pause
    exit /b 1
)

echo.
echo ========================================
echo RENAME COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Backup location: C:\Users\merce\Documents\%BACKUP_FOLDER%
echo New folder: C:\Users\merce\Documents\stellar-logic-ai
echo.
echo Next steps:
echo 1. Test critical functionality
echo 2. Run test suites
echo 3. Verify Git operations
echo 4. Update IDE workspace settings
echo.
pause
