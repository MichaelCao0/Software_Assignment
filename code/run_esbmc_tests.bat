@echo off
REM ESBMC形式化验证批处理脚本 (Windows)
REM 使用方法: run_esbmc_tests.bat

echo ============================================
echo ESBMC形式化验证测试套件
echo ============================================
echo.

REM 检查ESBMC是否安装
where esbmc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] ESBMC未安装或不在PATH中
    echo.
    echo 请选择以下安装方式之一:
    echo 1. 使用WSL: wsl --install, 然后在Ubuntu中安装ESBMC
    echo 2. 使用Docker: docker pull esbmc/esbmc:latest
    echo 3. 从源码编译: 参见 esbmc/BUILDING.md
    echo.
    echo 推荐使用WSL方式（最简单）:
    echo   wsl --install -d Ubuntu-22.04
    echo   wsl
    echo   sudo add-apt-repository ppa:esbmc/esbmc
    echo   sudo apt update
    echo   sudo apt install esbmc
    echo   pip install ast2json
    echo.
    pause
    exit /b 1
)

echo [信息] ESBMC已安装
esbmc --version
echo.

REM 检查测试文件是否存在
if not exist "esbmc_verification_tests.py" (
    echo [错误] 找不到测试文件: esbmc_verification_tests.py
    echo 请确保在正确的目录下运行此脚本
    pause
    exit /b 1
)

echo [信息] 开始运行验证测试...
echo.

set PASSED=0
set FAILED=0
set TOTAL=0

REM 定义测试列表
set TESTS=test_price_calculation_overflow test_subtotal_calculation test_quantity_update_bounds test_quantity_division_by_zero test_order_items_bounds_check test_cart_items_access test_rating_validation test_rating_boundary test_order_status_transition test_promotion_validity test_time_range_validation test_discount_calculation test_discount_overflow test_cart_concurrent_modification test_order_invariant

for %%t in (%TESTS%) do (
    echo.
    echo ========================================
    echo 测试: %%t
    echo ========================================
    
    set /a TOTAL+=1
    
    REM 运行ESBMC测试
    esbmc esbmc_verification_tests.py --function %%t --timeout 60
    
    if %ERRORLEVEL% EQU 0 (
        echo [√] %%t 通过
        set /a PASSED+=1
    ) else (
        echo [×] %%t 失败
        set /a FAILED+=1
    )
)

echo.
echo ============================================
echo 测试汇总
echo ============================================
echo 总计: %TOTAL%
echo 通过: %PASSED%
echo 失败: %FAILED%
echo ============================================
echo.

if %FAILED% EQU 0 (
    echo [成功] 所有测试通过！
    exit /b 0
) else (
    echo [警告] 有 %FAILED% 个测试失败
    echo 请查看上面的详细输出
    exit /b 1
)

pause



















