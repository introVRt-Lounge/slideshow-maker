@echo off
echo Creating CUDA 12 compatibility DLLs for ONNX Runtime...
echo.

copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublasLt64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublasLt64_12.dll"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy cublasLt64_13.dll
    goto :error
)

copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublas64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cublas64_12.dll"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy cublas64_13.dll
    goto :error
)

copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudart64_13.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cudart64_12.dll"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy cudart64_13.dll
    goto :error
)

copy "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cufft64_12.dll" "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin\x64\cufft64_11.dll"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy cufft64_12.dll
    goto :error
)

echo.
echo SUCCESS: All CUDA 12 compatibility DLLs created!
echo.
echo The following files were created:
echo - cublasLt64_12.dll (from cublasLt64_13.dll)
echo - cublas64_12.dll (from cublas64_13.dll)
echo - cudart64_12.dll (from cudart64_13.dll)
echo - cufft64_11.dll (from cufft64_12.dll)
echo.
echo Now restart your Python session and test GPU acceleration.
pause
exit /b 0

:error
echo.
echo Failed to create compatibility DLLs.
echo Make sure you're running this as Administrator.
pause
exit /b 1
