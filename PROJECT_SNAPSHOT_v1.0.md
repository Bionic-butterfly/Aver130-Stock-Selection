# 沪深300多因子选股系统 - 项目快照 v1.0

## 📅 快照时间
- **创建时间**: 2026-02-04
- **版本**: v1.0-base
- **状态**: 基础功能完整版本

## 🎯 项目概述
本项目是一个基于前后端分离架构的沪深300多因子选股系统，核心实现"行业中性化+XGBoost"多因子选股模型，并开发可视化演示系统。

## 📁 项目结构
```
Aver130/
├── quant_core/          # 量化核心模块
│   ├── config.py        # 配置文件
│   ├── data_loader.py   # 数据加载
│   ├── factor_processor.py # 因子处理
│   ├── model_trainer.py # 模型训练
│   ├── backtest_analyzer.py # 回测分析
│   ├── main.py          # 主程序
│   └── requirements.txt # 依赖列表
├── backend/             # 后端API服务
│   ├── main.py          # FastAPI主程序
│   └── requirements.txt # 依赖列表
├── frontend/            # 前端演示
│   ├── src/             # 源码目录
│   ├── dist/            # 静态演示页面
│   ├── package.json     # 依赖配置
│   └── vite.config.js   # 构建配置
├── data/                # 数据文件（运行时生成）
├── models/              # 模型文件（运行时生成）
├── run_quant.py         # 量化核心启动脚本
├── install_dependencies.py # 依赖安装脚本
├── setup_git.bat        # Git初始化脚本
├── backup_project.bat   # 项目备份脚本
└── README.md            # 项目说明
```

## ✅ 功能模块状态

### 1. 量化核心模块 (✅ 完整)
- **数据加载**: 模拟沪深300成分股数据，21,600条记录
- **因子处理**: 5个因子行业中性化处理
- **模型训练**: XGBoost模型训练，RMSE: 0.1005
- **回测分析**: Top 30/50/100策略对比

### 2. 后端API服务 (✅ 完整)
- **框架**: FastAPI 0.104.1
- **接口**: 完整的RESTful API
- **运行**: http://localhost:8000
- **文档**: http://localhost:8000/docs

### 3. 前端演示 (✅ 基础完整)
- **静态演示**: 无需Node.js的HTML页面
- **功能页面**: 数据概览、因子分析、回测对比
- **图表展示**: ECharts图表集成

## 🔧 技术栈

### 后端技术栈
- **Python**: 3.9
- **量化库**: pandas 1.5.3, numpy 1.23.5, scikit-learn 1.2.2, xgboost 1.7.6
- **Web框架**: FastAPI 0.104.1, uvicorn 0.24.0

### 前端技术栈
- **框架**: Vue 3.3.4
- **UI库**: Element Plus 2.4.4
- **图表**: ECharts 5.4.3
- **构建工具**: Vite

## 🚀 运行状态

### 量化核心运行结果
```
数据记录: 21,600条
因子数量: 5个 (PE、PB、ROE、换手率、总市值)
模型性能: RMSE 0.1005
最佳策略: Top 30 (超额收益5.4%)
```

### 后端服务状态
- **服务地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **模型加载**: XGBoost模型成功加载

## 📊 关键文件清单

### 核心代码文件
1. `quant_core/main.py` - 量化核心主程序
2. `backend/main.py` - 后端API服务
3. `frontend/dist/index.html` - 静态演示页面
4. `run_quant.py` - 量化核心启动脚本

### 配置文件
1. `quant_core/config.py` - 量化配置
2. `frontend/vite.config.js` - 前端构建配置
3. `package.json` - 前端依赖配置

### 工具脚本
1. `install_dependencies.py` - 依赖安装
2. `setup_git.bat` - Git初始化
3. `backup_project.bat` - 项目备份

## 🔄 版本控制信息

### Git状态 (如已初始化)
```bash
# 基础版本标签
v1.0-base: "基础功能完整版本：量化核心+后端API+前端静态演示"

# 提交信息
基础版本：沪深300多因子选股系统 - 前后端分离架构完成
```

### 备份信息
- **备份路径**: E:\Aver130_backup\Aver130_YYYYMMDD_HHMMSS
- **恢复方式**: 复制备份文件到项目目录

## 💡 后续开发指导

### 优化方向
1. **数据源优化**: 集成真实股票数据API
2. **算法优化**: 改进行业中性化算法
3. **前端优化**: 完善Vue组件和交互
4. **性能优化**: 添加缓存和异步处理

### 版本管理建议
1. **功能分支**: 每个新功能创建独立分支
2. **定期提交**: 重要修改及时提交
3. **版本标签**: 里程碑版本创建标签
4. **文档更新**: 同步更新项目文档

## 🎯 项目特色

1. **架构先进**: 严格的前后端分离架构
2. **算法创新**: 行业中性化+XGBoost多因子模型
3. **技术适配**: 完全适配本科生技术水平
4. **功能完整**: 量化全流程+可视化展示
5. **易于扩展**: 模块化设计便于功能扩展

---

**此快照记录了项目的基础版本状态，可作为后续开发的基准参考。**