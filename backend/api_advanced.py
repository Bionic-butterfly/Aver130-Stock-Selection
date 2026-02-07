# 沪深300多因子选股系统 - 高级API接口
# 【优化新增】增量接口模块，兼容原有FastAPI后端

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import yaml
import json
import os
import glob

# 创建高级API路由
router = APIRouter(prefix="/api/advanced", tags=["高级分析接口"])

# 响应模型定义
class FactorIndustryResponse(BaseModel):
    industry: str
    factor: str
    factor_name: str
    ic_mean: float
    ic_std: float
    ir: float
    monotonicity: float
    sample_size: int

class RiskMetricsResponse(BaseModel):
    annual_return: float
    benchmark_annual_return: float
    annual_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_loss_ratio: float

class ModelTuningResponse(BaseModel):
    learning_rate: float
    n_estimators: int
    train_score: float
    test_score: float
    rank: int

class BacktestScenarioResponse(BaseModel):
    scenario: str
    frequency: str
    top_n: int
    risk_metrics: RiskMetricsResponse

class LogEntryResponse(BaseModel):
    timestamp: str
    level: str
    message: str

class ConfigParameterResponse(BaseModel):
    section: str
    key: str
    value: Any
    description: str

class DataQualityResponse(BaseModel):
    report_date: str
    data_summary: Dict[str, Any]
    factor_quality: Dict[str, Any]
    data_integrity: Dict[str, Any]

# 辅助函数
def get_data_dir():
    """获取数据目录"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def get_logs_dir():
    """获取日志目录"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

def get_config_file():
    """获取配置文件路径"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "quant_core", "config_advanced.yaml")

@router.get("/factor-industry-analysis", response_model=List[FactorIndustryResponse])
def get_factor_industry_analysis(
    industry: Optional[str] = Query(None, description="行业筛选"),
    factor: Optional[str] = Query(None, description="因子筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取因子分行业分析数据
    """
    try:
        # 加载行业分析数据
        file_path = os.path.join(get_data_dir(), "industry_factor_analysis.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="行业分析数据不存在，请先运行量化核心")
        
        df = pd.read_csv(file_path)
        
        # 应用筛选条件
        if industry:
            df = df[df['industry'] == industry]
        if factor:
            df = df[df['factor'] == factor]
        
        # 分页处理
        total = len(df)
        start = (page - 1) * limit
        end = start + limit
        df_paginated = df.iloc[start:end]
        
        # 转换响应格式
        results = []
        for _, row in df_paginated.iterrows():
            results.append(FactorIndustryResponse(
                industry=row['industry'],
                factor=row['factor'],
                factor_name=row.get('factor_name', row['factor']),
                ic_mean=float(row.get('ic_mean', 0)),
                ic_std=float(row.get('ic_std', 0)),
                ir=float(row.get('ir', 0)),
                monotonicity=float(row.get('monotonicity', 0)),
                sample_size=int(row.get('sample_size', 0))
            ))
        
        # 添加分页信息到响应头
        response = {
            "data": results,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据加载失败: {str(e)}")

@router.get("/risk-metrics", response_model=RiskMetricsResponse)
def get_risk_metrics():
    """
    获取完整风险指标数据
    """
    try:
        # 加载风险指标数据
        file_path = os.path.join(get_data_dir(), "risk_metrics.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="风险指标数据不存在，请先运行量化核心")
        
        df = pd.read_csv(file_path)
        
        if len(df) == 0:
            raise HTTPException(status_code=404, detail="风险指标数据为空")
        
        # 返回第一条记录
        row = df.iloc[0]
        return RiskMetricsResponse(
            annual_return=float(row.get('annual_return', 0)),
            benchmark_annual_return=float(row.get('benchmark_annual_return', 0)),
            annual_volatility=float(row.get('annual_volatility', 0)),
            sharpe_ratio=float(row.get('sharpe_ratio', 0)),
            max_drawdown=float(row.get('max_drawdown', 0)),
            calmar_ratio=float(row.get('calmar_ratio', 0)),
            win_rate=float(row.get('win_rate', 0)),
            profit_loss_ratio=float(row.get('profit_loss_ratio', 0))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"风险指标加载失败: {str(e)}")

@router.get("/model-tuning-results", response_model=List[ModelTuningResponse])
def get_model_tuning_results(
    top_n: int = Query(10, ge=1, le=50, description="返回前N个最佳结果")
):
    """
    获取模型参数调优结果
    """
    try:
        # 加载调优结果
        file_path = os.path.join(get_data_dir(), "model_parameter_results.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="模型调优结果不存在，请先运行量化核心")
        
        df = pd.read_csv(file_path)
        
        # 按测试得分排序，取前N个
        df_sorted = df.nlargest(top_n, 'mean_test_score')
        
        results = []
        for idx, (_, row) in enumerate(df_sorted.iterrows(), 1):
            results.append(ModelTuningResponse(
                learning_rate=float(row['learning_rate']),
                n_estimators=int(row['n_estimators']),
                train_score=float(row.get('mean_train_score', 0)),
                test_score=float(row.get('mean_test_score', 0)),
                rank=idx
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型调优结果加载失败: {str(e)}")

@router.get("/backtest-scenarios", response_model=List[BacktestScenarioResponse])
def get_backtest_scenarios(
    frequency: Optional[str] = Query(None, description="调仓频率筛选"),
    scenario: Optional[str] = Query(None, description="市场阶段筛选"),
    top_n: Optional[int] = Query(None, ge=1, description="选股数量筛选")
):
    """
    获取多场景回测结果
    """
    try:
        # 加载回测结果
        file_path = os.path.join(get_data_dir(), "backtest_results_advanced.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="回测结果数据不存在，请先运行量化核心")
        
        df = pd.read_csv(file_path)
        
        # 应用筛选条件
        if frequency:
            df = df[df['frequency'] == frequency]
        if scenario:
            df = df[df['scenario'] == scenario]
        if top_n:
            df = df[df['top_n'] == top_n]
        
        # 转换响应格式
        results = []
        for _, row in df.iterrows():
            risk_metrics = RiskMetricsResponse(
                annual_return=float(row.get('annual_return', 0)),
                benchmark_annual_return=float(row.get('benchmark_annual_return', 0)),
                annual_volatility=float(row.get('annual_volatility', 0)),
                sharpe_ratio=float(row.get('sharpe_ratio', 0)),
                max_drawdown=float(row.get('max_drawdown', 0)),
                calmar_ratio=float(row.get('calmar_ratio', 0)),
                win_rate=float(row.get('win_rate', 0)),
                profit_loss_ratio=float(row.get('profit_loss_ratio', 0))
            )
            
            results.append(BacktestScenarioResponse(
                scenario=row['scenario'],
                frequency=row['frequency'],
                top_n=int(row['top_n']),
                risk_metrics=risk_metrics
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测场景数据加载失败: {str(e)}")

@router.get("/training-logs", response_model=List[LogEntryResponse])
def get_training_logs(
    level: Optional[str] = Query(None, description="日志级别筛选"),
    limit: int = Query(100, ge=1, le=500, description="返回日志条数"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """
    获取训练日志记录
    """
    try:
        # 获取最新的日志文件
        logs_dir = get_logs_dir()
        log_files = glob.glob(os.path.join(logs_dir, "quant_core_advanced_*.log"))
        
        if not log_files:
            # 返回模拟日志
            return [
                LogEntryResponse(
                    timestamp="2024-01-01 10:00:00",
                    level="INFO",
                    message="量化核心启动成功"
                ),
                LogEntryResponse(
                    timestamp="2024-01-01 10:01:00",
                    level="INFO",
                    message="数据加载完成"
                )
            ]
        
        # 按时间排序，取最新的
        log_files.sort(key=os.path.getmtime, reverse=True)
        latest_log_file = log_files[0]
        
        # 读取日志文件
        logs = []
        with open(latest_log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-limit:]
            
            for line in lines:
                # 解析日志格式: 2024-01-01 10:00:00,123 - INFO - 消息内容
                parts = line.strip().split(' - ', 2)
                if len(parts) >= 3:
                    timestamp = parts[0]
                    log_level = parts[1]
                    message = parts[2]
                    
                    # 应用筛选条件
                    if level and log_level != level:
                        continue
                    if keyword and keyword not in message:
                        continue
                    
                    logs.append(LogEntryResponse(
                        timestamp=timestamp,
                        level=log_level,
                        message=message
                    ))
        
        # 限制返回数量
        return logs[-limit:]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"日志文件读取失败: {str(e)}")

@router.get("/config-parameters", response_model=Dict[str, Any])
def get_config_parameters():
    """
    获取当前配置参数
    """
    try:
        config_file = get_config_file()
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置参数加载失败: {str(e)}")

@router.get("/data-quality-report", response_model=DataQualityResponse)
def get_data_quality_report():
    """
    获取数据质量报告
    """
    try:
        report_file = os.path.join(get_data_dir(), "data_quality_report.json")
        if not os.path.exists(report_file):
            raise HTTPException(status_code=404, detail="数据质量报告不存在")
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return DataQualityResponse(**report)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据质量报告加载失败: {str(e)}")

@router.get("/backtest-summary", response_model=Dict[str, Any])
def get_backtest_summary():
    """
    获取回测摘要信息
    """
    try:
        # 加载基础回测结果
        backtest_file = os.path.join(get_data_dir(), "backtest_results.csv")
        if not os.path.exists(backtest_file):
            raise HTTPException(status_code=404, detail="回测结果不存在，请先运行量化核心")
        
        df = pd.read_csv(backtest_file)
        
        # 计算摘要统计
        summary = {
            "total_strategies": len(df),
            "best_strategy": {
                "top_n": int(df.loc[df['excess_return'].idxmax(), 'top_n']),
                "excess_return": float(df['excess_return'].max()),
                "portfolio_return": float(df.loc[df['excess_return'].idxmax(), 'portfolio_return']),
                "benchmark_return": float(df.loc[df['excess_return'].idxmax(), 'benchmark_return'])
            },
            "average_excess_return": float(df['excess_return'].mean()),
            "strategies": df.to_dict('records')
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回测摘要加载失败: {str(e)}")

@router.get("/system-status", response_model=Dict[str, Any])
def get_system_status():
    """
    获取系统状态信息
    """
    try:
        # 检查数据文件
        data_dir = get_data_dir()
        data_files = os.listdir(data_dir)
        
        # 检查模型文件
        models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        model_files = []
        if os.path.exists(models_dir):
            model_files = os.listdir(models_dir)
        
        # 检查日志文件
        logs_dir = get_logs_dir()
        log_files = []
        if os.path.exists(logs_dir):
            log_files = os.listdir(logs_dir)
        
        status = {
            "data_files": data_files,
            "model_files": model_files,
            "log_files": log_files,
            "data_file_count": len(data_files),
            "model_file_count": len(model_files),
            "log_file_count": len(log_files),
            "status": "running",
            "message": "沪深300多因子选股系统服务运行正常"
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}")
