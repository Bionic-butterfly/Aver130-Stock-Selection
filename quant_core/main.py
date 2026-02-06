# 量化核心主程序
import pandas as pd
import os
from config import DATA_DIR
from data_loader import DataLoader
from factor_processor import FactorProcessor
from model_trainer import ModelTrainer
from backtest_analyzer import BacktestAnalyzer

def main():
    """量化核心主流程"""
    print("=== 沪深300多因子选股系统 - 量化核心模块 ===")
    print()
    
    # 1. 数据加载
    print("步骤1: 数据加载")
    print("-" * 50)
    loader = DataLoader()
    raw_data = loader.prepare_training_data()
    
    # 保存原始数据
    raw_data_path = os.path.join(DATA_DIR, 'raw_data.csv')
    raw_data.to_csv(raw_data_path, index=False)
    print(f"原始数据已保存: {raw_data_path}")
    print()
    
    # 2. 因子处理
    print("步骤2: 因子处理")
    print("-" * 50)
    processor = FactorProcessor()
    processed_data = processor.process_factors(raw_data)
    
    # 保存处理后的数据
    processed_data_path = os.path.join(DATA_DIR, 'processed_data.csv')
    processed_data.to_csv(processed_data_path, index=False)
    print(f"处理后的数据已保存: {processed_data_path}")
    
    # 计算因子IC值
    ic_results = processor.calculate_ic(processed_data)
    print("因子IC值分析:")
    for factor, ic in ic_results.items():
        print(f"  {factor}: {ic:.4f}")
    print()
    
    # 3. 模型训练
    print("步骤3: 模型训练")
    print("-" * 50)
    trainer = ModelTrainer()
    metrics = trainer.train_model(processed_data)
    
    print("模型训练结果:")
    print(f"  训练集RMSE: {metrics['train_rmse']:.4f}")
    print(f"  测试集RMSE: {metrics['test_rmse']:.4f}")
    print(f"  训练集R²: {metrics['train_r2']:.4f}")
    print(f"  测试集R²: {metrics['test_r2']:.4f}")
    
    # 绘制特征重要性
    importance_df = trainer.plot_feature_importance()
    print("特征重要性排序:")
    print(importance_df.to_string(index=False))
    print()
    
    # 4. 模型预测
    print("步骤4: 模型预测")
    print("-" * 50)
    prediction_results = trainer.predict(processed_data)
    
    # 保存预测结果
    prediction_path = os.path.join(DATA_DIR, 'prediction_results.csv')
    prediction_results.to_csv(prediction_path, index=False)
    print(f"预测结果已保存: {prediction_path}")
    print()
    
    # 5. 回测分析
    print("步骤5: 回测分析")
    print("-" * 50)
    analyzer = BacktestAnalyzer()
    backtest_results = analyzer.run_backtest(prediction_results)
    
    # 绘制回测图表
    analyzer.plot_performance_comparison()
    
    # 生成回测报告
    report = analyzer.generate_report()
    
    print("回测分析完成!")
    print("=" * 50)
    
    # 输出最终结果摘要
    print("\n=== 最终结果摘要 ===")
    best_result = backtest_results[50]  # 以Top 50为例
    print(f"选股策略: Top 50")
    print(f"组合收益率: {best_result['portfolio_return']:.4f}")
    print(f"基准收益率: {best_result['benchmark_return']:.4f}")
    print(f"超额收益: {best_result['excess_return']:.4f}")
    
    improvement = best_result['excess_return'] / abs(best_result['benchmark_return']) if best_result['benchmark_return'] != 0 else 0
    print(f"相对改进: {improvement:.2%}")
    
    return {
        'raw_data': raw_data_path,
        'processed_data': processed_data_path,
        'predictions': prediction_path,
        'backtest_results': backtest_results,
        'ic_results': ic_results,
        'model_metrics': metrics
    }

if __name__ == "__main__":
    try:
        results = main()
        print("\n量化核心模块执行完成!")
        print("所有输出文件已保存在data目录中")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()