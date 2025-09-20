@echo off
echo ====================================
echo CUDA PATH FIX ONLY
echo ====================================
echo.
echo This will update your system PATH to include CUDA bin\x64
echo Run this as Administrator to update system PATH
echo.

set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"

echo Current PATH check:
echo %PATH% | findstr /C:"%CUDA_PATH%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ CUDA path already exists in system PATH.
    goto :success
)

echo Adding CUDA path to system PATH...
setx PATH "%PATH%;%CUDA_PATH%" /M
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to update system PATH.
    echo Please make sure you're running this as Administrator.
    goto :error
)

echo.
echo ✅ SUCCESS: CUDA path added to system PATH!
echo.
echo The following path was added:
echo %CUDA_PATH%
echo.
echo Now you need to:
echo 1. Close ALL PowerShell/Command Prompt windows
echo 2. Open a NEW PowerShell/Command Prompt
echo 3. Navigate to your slideshow-maker directory
echo 4. Test GPU acceleration

goto :end

:success
echo.
echo CUDA path is already in system PATH.
echo You can proceed to test GPU acceleration.

:end
echo.
echo Test command:
echo python -c "from slideshow_maker.background_removal import BackgroundRemover; r = BackgroundRemover(); print('GPU WORKING!' if 'GPU' in str(r.session) else 'Still CPU')"
echo.
pause
exit /b 0

:error
echo.
echo ====================================
echo PATH UPDATE FAILED
echo ====================================
echo.
echo - Make sure you're running this as Administrator
echo - Check Windows permissions
echo.
pause
exit /b 1
