@echo off
echo ========================================
echo 沪深300多因子选股系统 - 高级版本部署脚本
echo ========================================

echo 步骤1: 检查Python环境
python --version
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.9
    pause
    exit /b 1
)

echo 步骤2: 安装Python依赖包
echo 安装后端依赖...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)
cd ..

echo 步骤3: 创建必要目录
if not exist data mkdir data
if not exist logs mkdir logs
if not exist reports mkdir reports
if not exist models mkdir models

echo 步骤4: 生成高级数据
echo 运行量化核心生成数据...
cd quant_core
python main_advanced.py
if errorlevel 1 (
    echo ❌ 数据生成失败
    pause
    exit /b 1
)
cd ..

echo 步骤5: 安装前端依赖
echo 安装前端依赖...
cd frontend
npm install
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
cd ..

echo 步骤6: 启动后端服务
echo 启动FastAPI后端服务...
start cmd /k "cd backend && python main.py"
timeout /t 5

echo 步骤7: 启动前端服务
echo 启动Vue3前端服务...
cd frontend
start cmd /k "npm run dev"
timeout /t 10

cd ..

echo.
echo ========================================
echo ✅ 部署完成！
echo ========================================
echo.
echo 📊 后端服务地址: http://localhost:8000
echo 🌐 前端服务地址: http://localhost:3000
echo 📄 API文档地址: http://localhost:8000/docs
echo.
echo 💡 使用说明:
echo 1. 后端服务将在端口8000运行
echo 2. 前端服务将在端口3000运行
echo 3. 访问前端页面开始使用系统
echo 4. 查看API文档了解接口详情
echo.
echo 注意: 请确保防火墙允许相关端口的访问
echo.

pause