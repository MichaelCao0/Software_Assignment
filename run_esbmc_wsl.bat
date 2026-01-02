@echo off
REM 通过WSL运行ESBMC验证
REM 使用方法: run_esbmc_wsl.bat [test_function_name]

echo ============================================
echo ESBMC WSL验证工具
echo ============================================
echo.

REM 检查WSL是否安装
wsl --status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] WSL未安装
    echo.
    echo 请运行以下命令安装WSL:
    echo   wsl --install -d Ubuntu-22.04
    echo.
    echo 安装完成后重启电脑，然后运行:
    echo   wsl
    echo   sudo add-apt-repository ppa:esbmc/esbmc
    echo   sudo apt update
    echo   sudo apt install esbmc
    echo   pip install ast2json
    echo.
    pause
    exit /b 1
)

echo [信息] WSL已安装
wsl --list --verbose
echo.

REM 转换Windows路径到WSL路径
set WIN_PATH=%CD%
set WSL_PATH=/mnt/%WIN_PATH::=%
set WSL_PATH=%WSL_PATH:\=/%
set WSL_PATH=%WSL_PATH:C=/c%
set WSL_PATH=%WSL_PATH:D=/d%
set WSL_PATH=%WSL_PATH:E=/e%

echo [信息] Windows路径: %WIN_PATH%
echo [信息] WSL路径: %WSL_PATH%
echo.

REM 检查ESBMC是否在WSL中安装
wsl bash -c "which esbmc" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] ESBMC未在WSL中安装
    echo.
    echo 请在WSL中运行以下命令安装ESBMC:
    echo   wsl
    echo   sudo add-apt-repository ppa:esbmc/esbmc
    echo   sudo apt update
    echo   sudo apt install esbmc
    echo   pip install ast2json
    echo.
    pause
    exit /b 1
)

echo [信息] ESBMC版本:
wsl bash -c "esbmc --version"
echo.

REM 如果提供了测试函数名
if "%~1"=="" (
    echo [信息] 运行所有测试...
    echo.
    
    REM 运行所有测试（简化版）
    set TESTS=test_price_calculation_overflow test_subtotal_calculation test_quantity_division_by_zero test_order_items_bounds_check test_rating_validation
    
    for %%t in (%TESTS%) do (
        echo.
        echo ======================================
        echo 测试: %%t
        echo ======================================
        wsl bash -c "cd '%WSL_PATH%' && esbmc esbmc_verification_tests.py --function %%t --timeout 30"
    )
    
) else (
    echo [信息] 运行测试: %~1
    echo.
    
    REM 运行指定测试
    wsl bash -c "cd '%WSL_PATH%' && esbmc esbmc_verification_tests.py --function %~1"
)

echo.
echo ============================================
echo 验证完成
echo ============================================
echo.

pause



















