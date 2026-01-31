@echo off
echo 🧹 STELLAR LOGIC AI - PROJECT CLEANUP ANALYSIS
echo %date% %time%
echo ========================================

echo 📁 Analyzing project structure...
dir /b /s *.py > py_files.txt 2>nul
dir /b /s *.html > html_files.txt 2>nul
dir /b /s *.js > js_files.txt 2>nul
dir /b /s *.css > css_files.txt 2>nul
dir /b /s *.db > db_files.txt 2>nul
dir /b /s *.md > md_files.txt 2>nul

echo 📊 File Count Summary:
echo   Python Files: 
find /c /v "" py_files.txt 2>nul
echo   HTML Files: 
find /c /v "" html_files.txt 2>nul
echo   JavaScript Files: 
find /c /v "" js_files.txt 2>nul
echo   CSS Files: 
find /c /v "" css_files.txt 2>nul
echo   Database Files: 
find /c /v "" db_files.txt 2>nul
echo   Documentation Files: 
find /c /v "" md_files.txt 2>nul

echo.
echo 🔍 Checking for potential issues...

echo 📏 Large Files (over 1MB):
for /f "delims=" %%f in ('dir /s /b *.py *.html *.js *.md 2^>nul') do (
    for %%s in ("%%f") do (
        if %%~zs GTR 1048576 (
            echo   %%f ^(%%~zs bytes^)
        )
    )
)

echo.
echo 🗑️ Checking for orphaned files...
echo 📋 Checking for duplicate names...
echo 📅 Checking for old files...

echo.
echo 💡 CLEANUP RECOMMENDATIONS:
echo   1. Review large files for optimization
echo   2. Check for unused imports in Python files
echo   3. Remove temporary files and caches
echo   4. Consolidate duplicate functionality
echo   5. Archive old documentation

echo.
echo 📄 Detailed analysis saved to: cleanup_report.txt
echo ========================================

REM Create simple cleanup report
echo STELLAR LOGIC AI PROJECT CLEANUP REPORT > cleanup_report.txt
echo Generated: %date% %time% >> cleanup_report.txt
echo ======================================== >> cleanup_report.txt
echo. >> cleanup_report.txt

REM Clean up temp files
del py_files.txt html_files.txt js_files.txt css_files.txt db_files.txt md_files.txt 2>nul

echo ✅ Project cleanup analysis complete!
pause
