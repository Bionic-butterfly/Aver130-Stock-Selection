# 沪深300多因子选股系统 - 高级量化核心主程序
# 【优化新增】整合所有高级模块，支持2019-2026年数据、分行业因子分析、参数调优、多场景回测

import pandas as pd
import os
import yaml
import logging
from datetime import datetime

# 导入高级模块
from data_loader_advanced import DataLoaderAdvanced
from factor_analyzer_advanced import FactorAnalyzerAdvanced
from model_trainer_advanced import ModelTrainerAdvanced
from backtest_analyzer_advanced import BacktestAnalyzerAdvanced

def setup_logging(config):
    """设置日志"""
    # 创建日志目录
    logs_dir = config['data']['logs_dir']
    os.makedirs(logs_dir, exist_ok=True)
    
    # 配置日志
    log_file = os.path.join(logs_dir, f'quant_core_advanced_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format=config['logging']['format'],
        datefmt=config['logging']['datefmt'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"日志已配置，保存到: {log_file}")
    return logger

def load_config(config_file='config_advanced.yaml'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        raise

def main():
    """量化核心主流程"""
    print("=== 沪深300多因子选股系统 - 高级量化核心模块 ===")
    print()
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    logger = setup_logging(config)
    logger.info("开始执行高级量化核心模块...")
    
    # 1. 数据加载
    logger.info("步骤1: 数据加载")
    print("步骤1: 数据加载")
    print("-" * 50)
    
    loader = DataLoaderAdvanced()
    raw_data = loader.prepare_training_data()
    
    # 保存原始数据
    raw_data_path = os.path.join(config['data']['data_dir'], 'raw_data.csv')
    raw_data.to_csv(raw_data_path, index=False)
    logger.info(f"原始数据已保存: {raw_data_path}")
    print(f"原始数据已保存: {raw_data_path}")
    print()
    
    # 2. 因子处理
    logger.info("步骤2: 因子处理")
    print("步骤2: 因子处理")
    print("-" * 50)
    
    analyzer = FactorAnalyzerAdvanced()
    processed_data = analyzer.process_factors(raw_data)
    
    # 保存处理后的数据
    processed_data_path = os.path.join(config['data']['data_dir'], config['data']['processed_data_file'])
    processed_data.to_csv(processed_data_path, index=False)
    logger.info(f"处理后的数据已保存: {processed_data_path}")
    print(f"处理后的数据已保存: {processed_data_path}")
    print()
    
    # 3. 因子分析
    logger.info("步骤3: 因子分析")
    print("步骤3: 因子分析")
    print("-" * 50)
    
    # 计算因子IC值
    ic_results = analyzer.calculate_ic(processed_data)
    print("因子IC值分析:")
    for factor, ic in ic_results.items():
        print(f"  {factor}: {ic:.4f}")
    print()
    
    # 计算因子IR信息比率
    ir_results = analyzer.calculate_ir(processed_data)
    print("因子IR信息比率分析:")
    for factor, ir in ir_results.items():
        print(f"  {factor}: {ir:.4f}")
    print()
    
    # 计算因子单调性
    monotonicity_results = analyzer.calculate_monotonicity(processed_data)
    print("因子分位数单调性分析:")
    for factor, monotonicity in monotonicity_results.items():
        print(f"  {factor}: {monotonicity:.4f}")
    print()
    
    # 生成因子分析报告
    factor_report = analyzer.generate_factor_report(processed_data)
    logger.info("因子分析报告生成完成")
    
    # 生成分行业因子分析数据
    industry_factor_data = loader.prepare_industry_factor_data(processed_data)
    logger.info("分行业因子分析数据生成完成")
    print()
    
    # 4. 模型训练
    logger.info("步骤4: 模型训练")
    print("步骤4: 模型训练")
    print("-" * 50)
    
    trainer = ModelTrainerAdvanced()
    metrics, model = trainer.train_model(processed_data)
    
    print("模型训练结果:")
    print(f"  训练集RMSE: {metrics['train_rmse']:.4f}")
    print(f"  测试集RMSE: {metrics['test_rmse']:.4f}")
    print(f"  训练集R²: {metrics['train_r2']:.4f}")
    print(f"  测试集R²: {metrics['test_r2']:.4f}")
    print()
    
    # 分析特征重要性
    feature_importance = trainer.analyze_feature_importance(model)
    print("特征重要性排序:")
    for factor, importance in feature_importance.items():
        print(f"  {factor}: {importance:.4f}")
    print()
    
    # 绘制特征重要性图表
    trainer.plot_feature_importance(model)
    
    # 5. 模型预测
    logger.info("步骤5: 模型预测")
    print("步骤5: 模型预测")
    print("-" * 50)
    
    prediction_results = trainer.predict(processed_data, model)
    
    # 保存预测结果
    prediction_path = os.path.join(config['data']['data_dir'], config['data']['prediction_results_file'])
    prediction_results.to_csv(prediction_path, index=False)
    logger.info(f"预测结果已保存: {prediction_path}")
    print(f"预测结果已保存: {prediction_path}")
    print()
    
    # 6. 回测分析
    logger.info("步骤6: 回测分析")
    print("步骤6: 回测分析")
    print("-" * 50)
    
    backtest_analyzer = BacktestAnalyzerAdvanced()
    backtest_results = backtest_analyzer.run_backtest(prediction_results)
    
    # 绘制回测图表
    backtest_analyzer.plot_performance_comparison()
    backtest_analyzer.plot_risk_metrics()
    
    # 生成回测报告
    report = backtest_analyzer.generate_report()
    logger.info("回测分析完成!")
    print("回测分析完成!")
    print("=" * 50)
    print()
    
    # 7. 输出最终结果摘要
    logger.info("步骤7: 输出最终结果摘要")
    print("=== 最终结果摘要 ===")
    
    # 最佳策略结果
    best_top_n = max(backtest_results, key=lambda x: backtest_results[x]['excess_return'])
    best_result = backtest_results[best_top_n]
    
    print(f"最佳选股策略: Top {best_top_n}")
    print(f"组合收益率: {best_result['portfolio_return']:.4f}")
    print(f"基准收益率: {best_result['benchmark_return']:.4f}")
    print(f"超额收益: {best_result['excess_return']:.4f}")
    print(f"相对改进: {best_result['improvement_ratio']:.2%}")
    print()
    
    # 模型性能
    print("=== 模型性能 ===")
    print(f"测试集R²: {metrics['test_r2']:.4f}")
    print(f"测试集RMSE: {metrics['test_rmse']:.4f}")
    print()
    
    # 因子分析结果
    print("=== 因子分析结果 ===")
    best_ic_factor = max(ic_results, key=ic_results.get)
    best_ir_factor = max(ir_results, key=ir_results.get)
    best_monotonicity_factor = max(monotonicity_results, key=monotonicity_results.get)
    
    print(f"最佳IC因子: {best_ic_factor} ({ic_results[best_ic_factor]:.4f})")
    print(f"最佳IR因子: {best_ir_factor} ({ir_results[best_ir_factor]:.4f})")
    print(f"最佳单调性因子: {best_monotonicity_factor} ({monotonicity_results[best_monotonicity_factor]:.4f})")
    print()
    
    # 特征重要性
    print("=== 特征重要性 ===")
    for i, (factor, importance) in enumerate(feature_importance.items(), 1):
        print(f"{i}. {factor}: {importance:.4f}")
    print()
    
    # 生成执行完成信息
    execution_info = {
        'status': 'completed',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'raw_data': raw_data_path,
        'processed_data': processed_data_path,
        'predictions': prediction_path,
        'backtest_results': backtest_results,
        'model_metrics': metrics,
        'factor_analysis': {
            'ic_results': ic_results,
            'ir_results': ir_results,
            'monotonicity_results': monotonicity_results
        },
        'feature_importance': feature_importance
    }
    
    logger.info("量化核心模块执行完成!")
    print("量化核心模块执行完成!")
    print("所有输出文件已保存在data目录中")
    print("所有图表已保存在models目录中")
    print("所有日志已保存在logs目录中")
    
    return execution_info

if __name__ == "__main__":
    try:
        results = main()
        print("\n执行结果摘要:")
        print(f"状态: {results['status']}")
        print(f"执行时间: {results['timestamp']}")
        print(f"最佳策略超额收益: {results['backtest_results'][max(results['backtest_results'], key=lambda x: results['backtest_results'][x]['excess_return'])]['excess_return']:.4f}")
        print(f"模型测试集R²: {results['model_metrics']['test_r2']:.4f}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
