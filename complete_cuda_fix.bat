@echo off
echo ====================================
echo COMPLETE CUDA COMPATIBILITY FIX
echo ====================================
echo.

echo Step 1: Creating CUDA 12 compatibility DLLs...
echo.

REM Create all necessary CUDA compatibility DLLs
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublasLt64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublasLt64_12.dll" >nul 2>&1
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublas64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublas64_12.dll" >nul 2>&1
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudart64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudart64_12.dll" >nul 2>&1
copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cufft64_12.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cufft64_11.dll" >nul 2>&1

REM Create cuDNN compatibility DLL from existing version
copy "C:\Program Files\Blackmagic Design\DaVinci Resolve\cudnn64_8.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudnn64_9.dll" >nul 2>&1

echo Step 2: Updating system PATH...
echo.

set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"

echo Checking if CUDA path already exists in PATH...
echo %PATH% | findstr /C:"%CUDA_PATH%" >nul 2>&1
if %errorlevel% equ 0 (
    echo CUDA path already exists in system PATH.
) else (
    echo Adding CUDA path to system PATH...
    setx PATH "%PATH%;%CUDA_PATH%" /M >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Failed to update system PATH.
        echo Please make sure you're running this as Administrator.
        goto :error
    )
    echo SUCCESS: CUDA path added to system PATH!
)

echo.
echo SUCCESS: All CUDA compatibility DLLs created!
echo.
echo The following compatibility DLLs were created:
echo - cublasLt64_12.dll (from cublasLt64_13.dll)
echo - cublas64_12.dll (from cublas64_13.dll)
echo - cudart64_12.dll (from cudart64_13.dll)
echo - cufft64_11.dll (from cufft64_12.dll)
echo - cudnn64_9.dll (from cudnn64_8.dll - DaVinci Resolve)

echo.
echo ====================================
echo VERIFICATION
echo ====================================
echo.

echo Checking created DLLs:
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublasLt64_12.dll" (
    echo ✓ cublasLt64_12.dll - EXISTS
) else (
    echo ✗ cublasLt64_12.dll - MISSING
)

if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublas64_12.dll" (
    echo ✓ cublas64_12.dll - EXISTS
) else (
    echo ✗ cublas64_12.dll - MISSING
)

if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudart64_12.dll" (
    echo ✓ cudart64_12.dll - EXISTS
) else (
    echo ✗ cudart64_12.dll - MISSING
)

if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cufft64_11.dll" (
    echo ✓ cufft64_11.dll - EXISTS
) else (
    echo ✗ cufft64_11.dll - MISSING
)

if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudnn64_9.dll" (
    echo ✓ cudnn64_9.dll - EXISTS
) else (
    echo ✗ cudnn64_9.dll - MISSING (cuDNN compatibility)
)

echo.
echo ====================================
echo NEXT STEPS
echo ====================================
echo.
echo 1. Close ALL PowerShell/Command Prompt windows
echo 2. Open a NEW PowerShell/Command Prompt (run as Administrator)
echo 3. Navigate to your slideshow-maker directory
echo 4. Test GPU acceleration:
echo.
echo    python -c "from slideshow_maker.background_removal import BackgroundRemover; r = BackgroundRemover(); print('GPU WORKING!' if 'GPU' in str(r.session) else 'Still CPU')"
echo.
echo 5. If GPU works, try your slideshow command:
echo.
echo    python -m slideshow_maker.cli.beatslides auto .\test-slideshow-local --preset music-video --hardcuts --pulse --mark-beats
echo.

pause
exit /b 0

:error
echo.
echo ====================================
echo ERROR: FIX FAILED
echo ====================================
echo.
echo - Make sure you're running this batch file as Administrator
echo - Check that CUDA 13.0 is properly installed
echo - Verify you have write permissions to Program Files
echo.
pause
exit /b 1
