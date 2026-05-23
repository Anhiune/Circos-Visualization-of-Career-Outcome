@echo off
REM Quick reference commands for generating Circos diagram on Windows

echo [Step 1] Generating data files from CSV...
python generate_circos_data.py

echo.
echo [Step 2] Navigating to circos directory...
cd circos

echo.
echo [Step 3] Running Circos...
REM Make sure circos is in your PATH, or use full path:
REM "C:\path\to\circos\bin\circos.exe" -conf circos.conf
circos -conf circos.conf

echo.
echo [Step 4] Checking output...
dir circos.png

echo.
echo Done! PNG file generated: circos.png
pause
