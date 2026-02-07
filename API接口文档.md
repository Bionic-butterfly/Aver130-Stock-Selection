# 沪深300多因子选股系统 - API接口文档

## 一、接口概述

本文档详细说明沪深300多因子选股系统的所有API接口，包括基础接口和高级接口。系统采用FastAPI框架开发，支持自动生成Swagger文档，可通过 `http://localhost:8000/docs` 访问交互式API文档。

## 二、基础接口

### 2.1 系统状态检查

**接口地址**: `/`
**请求方式**: GET
**功能描述**: 获取系统状态信息

**响应示例**:
```json
{
  "status": "running",
  "message": "沪深300多因子选股系统API服务运行中",
  "data_files": ["processed_data.csv", "prediction_results.csv"],
  "model_status": "loaded"
}
```

### 2.2 数据概览

**接口地址**: `/api/data/overview`
**请求方式**: GET
**功能描述**: 获取数据概览信息

**响应示例**:
```json
{
  "total_records": 10000,
  "date_range": {
    "start": "20190131",
    "end": "20260229"
  },
  "unique_stocks": 300,
  "industries": 28,
  "factors_available": ["pe_ttm_neutral_std", "pb_lf_neutral_std", "roe_neutral_std", "turnover_rate_neutral_std", "total_mv_neutral_std"]
}
```

### 2.3 因子IC值

**接口地址**: `/api/factors/ic`
**请求方式**: GET
**功能描述**: 获取因子IC值分析结果

**响应示例**:
```json
[
  {
    "factor": "pe_ttm",
    "ic_value": 0.0456,
    "description": "市盈率(TTM)"
  },
  {
    "factor": "pb_lf",
    "ic_value": 0.0321,
    "description": "市净率(LF)"
  },
  {
    "factor": "roe",
    "ic_value": 0.0678,
    "description": "净资产收益率"
  },
  {
    "factor": "turnover_rate",
    "ic_value": 0.0234,
    "description": "换手率"
  },
  {
    "factor": "total_mv",
    "ic_value": 0.0198,
    "description": "总市值"
  }
]
```

### 2.4 预测结果

**接口地址**: `/api/predictions/top/{top_n}`
**请求方式**: GET
**功能描述**: 获取Top N预测结果

**路径参数**:
- `top_n`: 整数，默认50，选股数量

**响应示例**:
```json
[
  {
    "ts_code": "000001.SZ",
    "predicted_return": 0.1567,
    "predicted_rank": 1,
    "industry": "银行"
  },
  {
    "ts_code": "000002.SZ",
    "predicted_return": 0.1432,
    "predicted_rank": 2,
    "industry": "房地产"
  }
]
```

### 2.5 回测结果

**接口地址**: `/api/backtest/results`
**请求方式**: GET
**功能描述**: 获取回测结果

**响应示例**:
```json
[
  {
    "top_n": 30,
    "portfolio_return": 0.152,
    "benchmark_return": 0.098,
    "excess_return": 0.054,
    "improvement_ratio": 0.551
  },
  {
    "top_n": 50,
    "portfolio_return": 0.145,
    "benchmark_return": 0.098,
    "excess_return": 0.047,
    "improvement_ratio": 0.48
  },
  {
    "top_n": 100,
    "portfolio_return": 0.128,
    "benchmark_return": 0.098,
    "excess_return": 0.03,
    "improvement_ratio": 0.306
  }
]
```

## 三、高级接口

### 3.1 因子分行业分析

**接口地址**: `/api/advanced/factor-industry-analysis`
**请求方式**: GET
**功能描述**: 获取因子分行业分析数据

**查询参数**:
- `industry`: 字符串，可选，行业筛选
- `factor`: 字符串，可选，因子筛选
- `page`: 整数，默认1，页码
- `limit`: 整数，默认20，每页数量

**响应示例**:
```json
[
  {
    "industry": "银行",
    "factor": "pe_ttm",
    "factor_name": "市盈率(TTM)",
    "ic_mean": 0.0456,
    "ic_std": 0.0123,
    "ir": 0.2345,
    "monotonicity": 0.789,
    "sample_size": 100
  },
  {
    "industry": "银行",
    "factor": "pb_lf",
    "factor_name": "市净率(LF)",
    "ic_mean": 0.0321,
    "ic_std": 0.0102,
    "ir": 0.1987,
    "monotonicity": 0.6543,
    "sample_size": 100
  }
]
```

### 3.2 风险指标详情

**接口地址**: `/api/advanced/risk-metrics`
**请求方式**: GET
**功能描述**: 获取完整风险指标数据

**响应示例**:
```json
{
  "annual_return": 0.1567,
  "benchmark_annual_return": 0.0987,
  "annual_volatility": 0.1234,
  "sharpe_ratio": 1.2345,
  "max_drawdown": 0.0876,
  "calmar_ratio": 1.789,
  "win_rate": 0.6543,
  "profit_loss_ratio": 1.8765
}
```

### 3.3 模型参数调优结果

**接口地址**: `/api/advanced/model-tuning-results`
**请求方式**: GET
**功能描述**: 获取XGBoost参数调优结果

**查询参数**:
- `top_n`: 整数，默认10，返回前N个最佳结果

**响应示例**:
```json
[
  {
    "learning_rate": 0.1,
    "n_estimators": 100,
    "train_score": 0.8765,
    "test_score": 0.789,
    "rank": 1
  },
  {
    "learning_rate": 0.05,
    "n_estimators": 150,
    "train_score": 0.8912,
    "test_score": 0.7765,
    "rank": 2
  }
]
```

### 3.4 多场景回测结果

**接口地址**: `/api/advanced/backtest-scenarios`
**请求方式**: GET
**功能描述**: 获取多场景回测结果

**查询参数**:
- `frequency`: 字符串，可选，调仓频率筛选（monthly/quarterly）
- `scenario`: 字符串，可选，市场阶段筛选（bull/bear/neutral）
- `top_n`: 整数，可选，选股数量筛选

**响应示例**:
```json
[
  {
    "scenario": "bull",
    "frequency": "monthly",
    "top_n": 50,
    "risk_metrics": {
      "annual_return": 0.2134,
      "benchmark_annual_return": 0.1567,
      "annual_volatility": 0.1456,
      "sharpe_ratio": 1.3456,
      "max_drawdown": 0.0987,
      "calmar_ratio": 2.163,
      "win_rate": 0.7123,
      "profit_loss_ratio": 2.1345
    }
  },
  {
    "scenario": "bear",
    "frequency": "monthly",
    "top_n": 50,
    "risk_metrics": {
      "annual_return": -0.0567,
      "benchmark_annual_return": -0.1234,
      "annual_volatility": 0.1678,
      "sharpe_ratio": -0.2134,
      "max_drawdown": 0.1876,
      "calmar_ratio": -0.302,
      "win_rate": 0.4567,
      "profit_loss_ratio": 0.8765
    }
  }
]
```

### 3.5 训练日志

**接口地址**: `/api/advanced/training-logs`
**请求方式**: GET
**功能描述**: 获取训练日志记录

**查询参数**:
- `level`: 字符串，可选，日志级别筛选（INFO/WARNING/ERROR）
- `limit`: 整数，默认100，返回日志条数
- `keyword`: 字符串，可选，关键词搜索

**响应示例**:
```json
[
  {
    "timestamp": "2026-02-07 10:00:00",
    "level": "INFO",
    "message": "量化核心启动成功"
  },
  {
    "timestamp": "2026-02-07 10:01:00",
    "level": "INFO",
    "message": "数据加载完成，共10000条记录"
  }
]
```

### 3.6 配置参数

**接口地址**: `/api/advanced/config-parameters`
**请求方式**: GET
**功能描述**: 获取当前配置参数

**响应示例**:
```json
{
  "basic": {
    "project_name": "沪深300多因子选股系统",
    "version": "2.0",
    "start_date": "2019-01-01",
    "end_date": "2026-02-05",
    "description": "基于XGBoost的行业中性多因子选股模型"
  },
  "factors": {
    "selected_factors": ["pe_ttm", "pb_lf", "roe", "turnover_rate", "total_mv"],
    "factor_names": {
      "pe_ttm": "市盈率(TTM)",
      "pb_lf": "市净率(LF)",
      "roe": "净资产收益率",
      "turnover_rate": "换手率",
      "total_mv": "总市值"
    }
  }
}
```

### 3.7 数据质量报告

**接口地址**: `/api/advanced/data-quality-report`
**请求方式**: GET
**功能描述**: 获取数据质量报告

**响应示例**:
```json
{
  "report_date": "2026-02-07 10:00:00",
  "data_summary": {
    "total_records": 10000,
    "unique_stocks": 300,
    "unique_industries": 28,
    "date_range": {
      "start": "20190131",
      "end": "20260229"
    }
  },
  "factor_quality": {
    "pe_ttm": {
      "mean": 15.6789,
      "std": 8.9123,
      "min": 3.4567,
      "max": 45.6789,
      "missing_values": 0
    }
  },
  "data_integrity": {
    "missing_values": {
      "trade_date": 0,
      "ts_code": 0,
      "industry": 0,
      "future_return": 0,
      "pe_ttm": 0
    },
    "duplicate_records": 0
  }
}
```

### 3.8 回测摘要

**接口地址**: `/api/advanced/backtest-summary`
**请求方式**: GET
**功能描述**: 获取回测摘要信息

**响应示例**:
```json
{
  "total_strategies": 3,
  "best_strategy": {
    "top_n": 30,
    "excess_return": 0.054,
    "portfolio_return": 0.152,
    "benchmark_return": 0.098
  },
  "average_excess_return": 0.0437,
  "strategies": [
    {
      "top_n": 30,
      "portfolio_return": 0.152,
      "benchmark_return": 0.098,
      "excess_return": 0.054,
      "improvement_ratio": 0.551
    }
  ]
}
```

### 3.9 系统状态

**接口地址**: `/api/advanced/system-status`
**请求方式**: GET
**功能描述**: 获取系统状态信息

**响应示例**:
```json
{
  "data_files": ["processed_data.csv", "prediction_results.csv"],
  "model_files": ["xgboost_model_best.pkl", "xgboost_model_base.pkl"],
  "log_files": ["quant_core_advanced_20260207_100000.log"],
  "data_file_count": 10,
  "model_file_count": 5,
  "log_file_count": 3,
  "status": "running",
  "message": "沪深300多因子选股系统服务运行正常"
}
```

## 四、响应状态码

| 状态码 | 描述 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |

## 五、接口规范

1. **请求格式**: 所有API接口支持GET请求，部分接口支持POST请求
2. **响应格式**: 统一返回JSON格式数据
3. **错误处理**: 错误时返回标准错误格式，包含错误码和错误信息
4. **参数验证**: 所有参数会进行类型和范围验证
5. **分页支持**: 支持分页的接口使用page和limit参数
6. **筛选支持**: 支持筛选的接口使用相应的查询参数

## 六、使用示例

### 6.1 获取因子分行业分析数据

```bash
# 获取所有行业所有因子的分析数据
curl http://localhost:8000/api/advanced/factor-industry-analysis

# 筛选银行行业的数据
curl http://localhost:8000/api/advanced/factor-industry-analysis?industry=银行

# 筛选市盈率因子的数据
curl http://localhost:8000/api/advanced/factor-industry-analysis?factor=pe_ttm

# 分页获取数据
curl http://localhost:8000/api/advanced/factor-industry-analysis?page=2&limit=10
```

### 6.2 获取多场景回测结果

```bash
# 获取所有场景的回测结果
curl http://localhost:8000/api/advanced/backtest-scenarios

# 筛选月度调仓的数据
curl http://localhost:8000/api/advanced/backtest-scenarios?frequency=monthly

# 筛选牛市场景的数据
curl http://localhost:8000/api/advanced/backtest-scenarios?scenario=bull

# 筛选Top 50选股的数据
curl http://localhost:8000/api/advanced/backtest-scenarios?top_n=50
```

### 6.3 获取训练日志

```bash
# 获取最近100条日志
curl http://localhost:8000/api/advanced/training-logs

# 获取INFO级别的日志
curl http://localhost:8000/api/advanced/training-logs?level=INFO

# 搜索包含"模型"的日志
curl http://localhost:8000/api/advanced/training-logs?keyword=模型

# 限制返回50条日志
curl http://localhost:8000/api/advanced/training-logs?limit=50
```

## 七、注意事项

1. **接口性能**: 部分接口（如因子分行业分析）可能返回大量数据，建议使用分页参数
2. **数据更新**: 接口返回的数据依赖于量化核心模块的运行结果，需要先运行量化核心生成数据
3. **参数验证**: 请确保传入的参数符合接口要求，否则会返回400错误
4. **错误处理**: 遇到错误时，请查看响应中的错误信息，根据提示进行调整
5. **版本兼容性**: 接口设计考虑了向后兼容性，不会破坏现有调用

## 八、接口变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-02-07 | 新增高级接口，支持分行业因子分析、风险指标详情、模型参数调优、多场景回测等 |
| v1.0 | 2024-01-01 | 基础接口，支持系统状态、数据概览、因子IC值、预测结果、回测结果等 |

---

**文档更新时间**: 2026-02-07
**文档版本**: v2.0
**适用系统版本**: v2.0+
