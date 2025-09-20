@echo off
echo Adding CUDA bin\x64 directory to system PATH for GPU acceleration...
echo.

set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64"

echo Checking if CUDA path already exists in PATH...
echo %PATH% | findstr /C:"%CUDA_PATH%" >nul
if %errorlevel% equ 0 (
    echo CUDA path already exists in PATH.
    goto :success
)

echo Adding CUDA path to system PATH...
setx PATH "%PATH%;%CUDA_PATH%" /M
if %errorlevel% neq 0 (
    echo ERROR: Failed to update system PATH.
    echo Make sure you're running this as Administrator.
    goto :error
)

echo.
echo SUCCESS: CUDA path added to system PATH!
echo.
echo The following path was added:
echo %CUDA_PATH%
echo.
echo Please restart your command prompt/PowerShell and test GPU acceleration.
pause
goto :end

:success
echo.
echo CUDA path is already in system PATH.
echo You can proceed to test GPU acceleration.
pause
goto :end

:error
echo.
echo Failed to update PATH.
pause
exit /b 1

:end
exit /b 0
