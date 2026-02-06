# 后端API主程序
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os
from typing import List, Dict, Any
import uvicorn

# 导入量化核心模块
import sys
sys.path.append('../quant_core')
from config import DATA_DIR, MODEL_DIR

app = FastAPI(
    title="沪深300多因子选股系统API",
    description="基于行业中性化+XGBoost的多因子选股系统后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型定义
class FactorICResponse(BaseModel):
    factor: str
    ic_value: float
    description: str

class StockPrediction(BaseModel):
    ts_code: str
    predicted_return: float
    predicted_rank: int
    industry: str

class BacktestResult(BaseModel):
    top_n: int
    portfolio_return: float
    benchmark_return: float
    excess_return: float
    improvement_ratio: float

class SystemStatus(BaseModel):
    status: str
    message: str
    data_files: List[str]
    model_status: str

# 全局变量
model = None
feature_columns = []

# 初始化函数
@app.on_event("startup")
async def startup_event():
    """启动时加载模型和数据"""
    global model, feature_columns
    
    try:
        # 加载模型
        model_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print("XGBoost模型加载成功")
        else:
            print("警告: 未找到预训练模型，请先运行量化核心模块")
        
        # 设置特征列
        feature_columns = [f'{factor}_neutral_std' for factor in ['pe_ttm', 'pb_lf', 'roe', 'turnover_rate', 'total_mv']]
        
    except Exception as e:
        print(f"启动时发生错误: {e}")

# API路由
@app.get("/", response_model=SystemStatus)
async def root():
    """系统状态检查"""
    # 检查数据文件
    data_files = []
    if os.path.exists(DATA_DIR):
        data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    return SystemStatus(
        status="running" if model else "model_not_loaded",
        message="沪深300多因子选股系统API服务运行中",
        data_files=data_files,
        model_status="loaded" if model else "not_loaded"
    )

@app.get("/api/factors/ic", response_model=List[FactorICResponse])
async def get_factor_ic():
    """获取因子IC值"""
    try:
        data_path = os.path.join(DATA_DIR, 'processed_data.csv')
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="处理后的数据文件不存在")
        
        df = pd.read_csv(data_path)
        
        # 计算IC值
        ic_results = []
        factors = ['pe_ttm', 'pb_lf', 'roe', 'turnover_rate', 'total_mv']
        
        for factor in factors:
            neutral_factor = f'{factor}_neutral_std'
            if neutral_factor in df.columns:
                ic = df[neutral_factor].corr(df['future_return'])
                
                # 因子描述映射
                desc_map = {
                    'pe_ttm': '市盈率(TTM)',
                    'pb_lf': '市净率(LF)',
                    'roe': '净资产收益率',
                    'turnover_rate': '换手率',
                    'total_mv': '总市值'
                }
                
                ic_results.append(FactorICResponse(
                    factor=factor,
                    ic_value=float(ic),
                    description=desc_map.get(factor, factor)
                ))
        
        return ic_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取因子IC值时出错: {str(e)}")

@app.get("/api/predictions/top/{top_n}", response_model=List[StockPrediction])
async def get_top_predictions(top_n: int = 50):
    """获取Top N预测结果"""
    try:
        data_path = os.path.join(DATA_DIR, 'prediction_results.csv')
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="预测结果文件不存在")
        
        df = pd.read_csv(data_path)
        
        # 获取Top N预测结果
        top_stocks = df.nlargest(top_n, 'predicted_return')
        
        predictions = []
        for _, row in top_stocks.iterrows():
            predictions.append(StockPrediction(
                ts_code=row['ts_code'],
                predicted_return=float(row['predicted_return']),
                predicted_rank=int(row['predicted_rank']),
                industry=row.get('industry', '未知')
            ))
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预测结果时出错: {str(e)}")

@app.get("/api/backtest/results", response_model=List[BacktestResult])
async def get_backtest_results():
    """获取回测结果"""
    try:
        report_path = os.path.join(DATA_DIR, 'backtest_report.csv')
        if not os.path.exists(report_path):
            # 如果没有报告文件，生成模拟数据
            return generate_sample_backtest_results()
        
        df = pd.read_csv(report_path)
        
        results = []
        for _, row in df.iterrows():
            results.append(BacktestResult(
                top_n=int(row['top_n']),
                portfolio_return=float(row['portfolio_return']),
                benchmark_return=float(row['benchmark_return']),
                excess_return=float(row['excess_return']),
                improvement_ratio=float(row.get('improvement_ratio', 0))
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回测结果时出错: {str(e)}")

def generate_sample_backtest_results():
    """生成示例回测结果（用于演示）"""
    return [
        BacktestResult(
            top_n=30,
            portfolio_return=0.152,
            benchmark_return=0.098,
            excess_return=0.054,
            improvement_ratio=0.551
        ),
        BacktestResult(
            top_n=50,
            portfolio_return=0.145,
            benchmark_return=0.098,
            excess_return=0.047,
            improvement_ratio=0.480
        ),
        BacktestResult(
            top_n=100,
            portfolio_return=0.128,
            benchmark_return=0.098,
            excess_return=0.030,
            improvement_ratio=0.306
        )
    ]

@app.get("/api/data/overview")
async def get_data_overview():
    """获取数据概览"""
    try:
        data_path = os.path.join(DATA_DIR, 'processed_data.csv')
        if not os.path.exists(data_path):
            return {"message": "数据文件不存在，请先运行量化核心模块"}
        
        df = pd.read_csv(data_path)
        
        return {
            "total_records": len(df),
            "date_range": {
                "start": df['trade_date'].min(),
                "end": df['trade_date'].max()
            },
            "unique_stocks": df['ts_code'].nunique(),
            "industries": df['industry'].nunique() if 'industry' in df.columns else 0,
            "factors_available": [col for col in df.columns if 'neutral_std' in col]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据概览时出错: {str(e)}")

@app.post("/api/predict/custom")
async def predict_custom_stocks(factor_data: List[Dict[str, Any]]):
    """自定义股票预测"""
    if model is None:
        raise HTTPException(status_code=400, detail="模型未加载，无法进行预测")
    
    try:
        predictions = []
        
        for stock_data in factor_data:
            # 准备特征数据
            features = []
            for factor in ['pe_ttm', 'pb_lf', 'roe', 'turnover_rate', 'total_mv']:
                feature_name = f'{factor}_neutral_std'
                features.append(stock_data.get(feature_name, 0))
            
            # 预测
            prediction = model.predict([features])[0]
            
            predictions.append({
                "ts_code": stock_data.get("ts_code", "未知"),
                "predicted_return": float(prediction),
                "factors": stock_data
            })
        
        # 按预测收益率排序
        predictions.sort(key=lambda x: x["predicted_return"], reverse=True)
        
        # 添加排名
        for i, pred in enumerate(predictions):
            pred["rank"] = i + 1
        
        return {"predictions": predictions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测时出错: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )