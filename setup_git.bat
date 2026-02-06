@echo off
echo ========================================
echo   沪深300多因子选股系统 - Git初始化
echo ========================================
echo.

REM 检查是否已安装Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo ✅ Git版本: 
git --version
echo.

REM 初始化Git仓库
echo 🔄 正在初始化Git仓库...
git init
if %errorlevel% neq 0 (
    echo ❌ Git初始化失败
    pause
    exit /b 1
)
echo ✅ Git仓库初始化成功
echo.

REM 添加文件到暂存区
echo 🔄 正在添加文件到暂存区...
git add .
echo ✅ 文件添加完成
echo.

REM 创建基础版本提交
echo 🔄 正在创建基础版本提交...
git commit -m "基础版本：沪深300多因子选股系统 - 前后端分离架构完成"
if %errorlevel% neq 0 (
    echo ❌ 提交失败，请检查Git配置
    echo 请配置用户名和邮箱：
    echo git config --global user.name "您的姓名"
    echo git config --global user.email "您的邮箱"
    pause
    exit /b 1
)
echo ✅ 基础版本提交完成
echo.

REM 创建版本标签
echo 🔄 正在创建版本标签...
git tag -a "v1.0-base" -m "基础功能完整版本：量化核心+后端API+前端静态演示"
echo ✅ 版本标签创建完成
echo.

REM 显示Git状态
echo 📊 Git仓库状态：
git status
echo.
git log --oneline -5
echo.

echo ========================================
echo 🎉 Git版本控制设置完成！
echo ========================================
echo.
echo 📋 常用Git命令：
echo   查看状态: git status
echo   查看提交历史: git log --oneline
echo   创建新分支: git checkout -b 新分支名
echo   回退到基础版本: git checkout v1.0-base
echo   比较差异: git diff
echo.
echo 💡 后续开发建议：
echo   1. 每次重要修改前创建新分支
echo   2. 定期提交代码并添加有意义的提交信息
echo   3. 重要里程碑创建版本标签
echo.
pause