@echo off
REM 使用Docker运行ESBMC验证
REM 使用方法: run_esbmc_docker.bat [test_function_name]

echo ============================================
echo ESBMC Docker验证工具
echo ============================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Docker未安装
    echo 请先安装Docker Desktop for Windows
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [信息] Docker已安装
docker --version
echo.

REM 获取当前目录
set CURRENT_DIR=%CD%

REM 如果提供了测试函数名
if "%~1"=="" (
    echo [信息] 运行所有测试...
    echo.
    
    REM 运行所有测试
    docker run --rm -v "%CURRENT_DIR%:/data" esbmc/esbmc:latest ^
        bash -c "cd /data && python3 -m pip install ast2json && esbmc esbmc_verification_tests.py"
    
) else (
    echo [信息] 运行测试: %~1
    echo.
    
    REM 运行指定测试
    docker run --rm -v "%CURRENT_DIR%:/data" esbmc/esbmc:latest ^
        bash -c "cd /data && python3 -m pip install ast2json && esbmc esbmc_verification_tests.py --function %~1"
)

echo.
echo ============================================
echo 验证完成
echo ============================================
echo.

pause



















