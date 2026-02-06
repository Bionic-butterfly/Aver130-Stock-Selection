@echo off
echo ========================================
echo   沪深300多因子选股系统 - 项目备份
echo ========================================
echo.

REM 设置备份目录
set "backup_dir=E:\Aver130_backup"
set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=%timestamp: =0%"
set "backup_path=%backup_dir%\Aver130_%timestamp%"

REM 创建备份目录
if not exist "%backup_dir%" mkdir "%backup_dir%"
if not exist "%backup_path%" mkdir "%backup_path%"

echo 📁 备份目录: %backup_path%
echo.

REM 备份核心代码文件
echo 🔄 正在备份核心代码文件...

REM 备份量化核心模块
xcopy "quant_core" "%backup_path%\quant_core" /E /I /Y
if %errorlevel% neq 0 echo ⚠️ 量化核心备份可能有问题

REM 备份后端模块
xcopy "backend" "%backup_path%\backend" /E /I /Y
if %errorlevel% neq 0 echo ⚠️ 后端模块备份可能有问题

REM 备份前端模块
xcopy "frontend" "%backup_path%\frontend" /E /I /Y
if %errorlevel% neq 0 echo ⚠️ 前端模块备份可能有问题

REM 备份配置和脚本文件
copy "run_quant.py" "%backup_path%\" >nul
copy "install_dependencies.py" "%backup_path%\" >nul
copy "README.md" "%backup_path%\" >nul
copy ".gitignore" "%backup_path%\" >nul
copy "setup_git.bat" "%backup_path%\" >nul

echo ✅ 文件备份完成
echo.

REM 创建备份信息文件
echo 备份时间: %date% %time% > "%backup_path%\backup_info.txt"
echo 备份版本: 基础版本 v1.0 >> "%backup_path%\backup_info.txt"
echo 项目状态: 前后端分离架构完成 >> "%backup_path%\backup_info.txt"
echo 功能模块: >> "%backup_path%\backup_info.txt"
echo   - 量化核心: 数据加载+因子处理+模型训练+回测分析 >> "%backup_path%\backup_info.txt"
echo   - 后端API: FastAPI服务+所有接口 >> "%backup_path%\backup_info.txt"
echo   - 前端演示: 静态页面+图表展示 >> "%backup_path%\backup_info.txt"

echo 📄 备份信息已保存
echo.

REM 显示备份结果
dir "%backup_path%" /B
echo.

echo ========================================
echo 🎉 项目备份完成！
echo ========================================
echo.
echo 📊 备份统计：
for /f %%i in ('dir "%backup_path%" /S /B ^| find /c /v ""') do echo 文件数量: %%i
echo 备份大小: 
forfiles /p "%backup_path%" /s /c "cmd /c echo @fsize" | awk "{sum+=$1} END {print sum/1024/1024 \" MB\"}"
echo.

echo 💡 恢复说明：
echo   如需恢复此版本，请将备份目录中的文件复制回项目目录
echo   备份路径: %backup_path%
echo.

echo 📋 备份文件列表：
tree "%backup_path%" /F | more
echo.
pause