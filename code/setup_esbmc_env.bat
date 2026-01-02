@echo off
REM ESBMC环境配置脚本
REM 安装必要的Python依赖

echo ============================================
echo ESBMC Python Frontend 环境配置
echo ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] Python未安装
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo [信息] Python版本:
python --version
echo.

echo [步骤1] 安装ast2json模块...
echo ----------------------------------------
pip install ast2json
echo.

if %ERRORLEVEL% EQU 0 (
    echo [成功] ast2json已安装
) else (
    echo [错误] ast2json安装失败
    pause
    exit /b 1
)

echo.
echo [步骤2] 验证安装...
echo ----------------------------------------
python -c "import ast2json; print('✓ ast2json version:', ast2json.__version__ if hasattr(ast2json, '__version__') else 'unknown')"

echo.
echo [步骤3] 测试JSON生成工具...
echo ----------------------------------------
if exist generate_ast_json.py (
    echo ✓ generate_ast_json.py 存在
    python generate_ast_json.py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo ✓ JSON生成工具可用
    ) else (
        echo ⚠ JSON生成工具运行异常（可能是参数问题，这是正常的）
    )
) else (
    echo [警告] generate_ast_json.py 不存在
)

echo.
echo ============================================
echo 环境配置完成！
echo ============================================
echo.
echo 下一步：
echo 1. 生成AST JSON：
echo    python generate_ast_json.py esbmc_verification_tests.py
echo.
echo 2. 安装ESBMC（选择一种方式）：
echo    - WSL: 参见 ESBMC快速开始指南.md
echo    - Docker: docker pull esbmc/esbmc:latest
echo.
echo 3. 运行验证：
echo    run_esbmc_wsl.bat test_price_calculation_overflow
echo ============================================
echo.

pause



















