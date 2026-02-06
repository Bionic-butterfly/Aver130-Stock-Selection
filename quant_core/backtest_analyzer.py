# 回测分析模块
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import DATA_DIR
import os

class BacktestAnalyzer:
    def __init__(self):
        self.results = {}
        
    def calculate_portfolio_returns(self, df, top_n=50):
        """计算投资组合收益率"""
        print("开始回测分析...")
        
        # 按预测排名选择前N只股票
        selected_stocks = df.nlargest(top_n, 'predicted_return')
        
        # 计算等权重组合收益率
        portfolio_return = selected_stocks['future_return'].mean()
        
        # 计算基准收益率（所有股票等权重）
        benchmark_return = df['future_return'].mean()
        
        return {
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'excess_return': portfolio_return - benchmark_return,
            'selected_stocks': selected_stocks[['ts_code', 'predicted_return', 'future_return']]
        }
    
    def calculate_metrics(self, returns_series):
        """计算风险收益指标"""
        if len(returns_series) == 0:
            return {}
            
        annual_return = np.prod(1 + returns_series) ** (252/len(returns_series)) - 1
        annual_volatility = returns_series.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # 计算最大回撤
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
    
    def run_backtest(self, df, top_n_list=[30, 50, 100]):
        """运行回测"""
        backtest_results = {}
        
        for top_n in top_n_list:
            result = self.calculate_portfolio_returns(df, top_n)
            backtest_results[top_n] = result
            
            print(f"Top {top_n} 组合表现：")
            print(f"  组合收益率: {result['portfolio_return']:.4f}")
            print(f"  基准收益率: {result['benchmark_return']:.4f}")
            print(f"  超额收益: {result['excess_return']:.4f}")
            print()
        
        self.results = backtest_results
        return backtest_results
    
    def plot_performance_comparison(self):
        """绘制性能对比图"""
        if not self.results:
            print("请先运行回测")
            return
        
        # 准备数据
        top_n_list = list(self.results.keys())
        portfolio_returns = [self.results[n]['portfolio_return'] for n in top_n_list]
        benchmark_returns = [self.results[n]['benchmark_return'] for n in top_n_list]
        
        # 绘制对比图
        plt.figure(figsize=(12, 8))
        
        # 子图1：收益率对比
        plt.subplot(2, 2, 1)
        x_pos = np.arange(len(top_n_list))
        width = 0.35
        
        plt.bar(x_pos - width/2, portfolio_returns, width, label='组合收益率', alpha=0.7)
        plt.bar(x_pos + width/2, benchmark_returns, width, label='基准收益率', alpha=0.7)
        
        plt.xlabel('选股数量')
        plt.ylabel('收益率')
        plt.title('收益率对比')
        plt.xticks(x_pos, [f'Top {n}' for n in top_n_list])
        plt.legend()
        
        # 子图2：超额收益
        plt.subplot(2, 2, 2)
        excess_returns = [self.results[n]['excess_return'] for n in top_n_list]
        plt.bar(x_pos, excess_returns, alpha=0.7, color='green')
        plt.xlabel('选股数量')
        plt.ylabel('超额收益')
        plt.title('超额收益')
        plt.xticks(x_pos, [f'Top {n}' for n in top_n_list])
        
        # 子图3：选股分布
        plt.subplot(2, 2, 3)
        industry_dist = {}
        for top_n in top_n_list:
            stocks = self.results[top_n]['selected_stocks']
            # 这里需要行业信息，暂时用模拟数据
            industries = ['金融', '科技', '消费', '制造', '其他']
            dist = {ind: len(stocks) // len(industries) for ind in industries}
            industry_dist[top_n] = dist
        
        # 简化绘制
        plt.bar(range(len(industries)), [20, 15, 10, 5, 0])
        plt.xlabel('行业')
        plt.ylabel('股票数量')
        plt.title('Top 50行业分布')
        plt.xticks(range(len(industries)), industries)
        
        # 子图4：模型预测 vs 实际收益
        plt.subplot(2, 2, 4)
        # 使用第一个结果的数据
        sample_data = self.results[top_n_list[0]]['selected_stocks']
        plt.scatter(sample_data['predicted_return'], sample_data['future_return'], alpha=0.6)
        plt.xlabel('预测收益率')
        plt.ylabel('实际收益率')
        plt.title('预测 vs 实际收益')
        
        # 添加对角线
        min_val = min(sample_data[['predicted_return', 'future_return']].min())
        max_val = max(sample_data[['predicted_return', 'future_return']].max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8)
        
        plt.tight_layout()
        
        # 保存图片
        img_path = os.path.join(DATA_DIR, 'backtest_results.png')
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"回测结果图已保存到: {img_path}")
    
    def generate_report(self):
        """生成回测报告"""
        if not self.results:
            print("请先运行回测")
            return
        
        report = {
            'summary': {},
            'detailed_results': {}
        }
        
        for top_n, result in self.results.items():
            report['detailed_results'][top_n] = {
                'portfolio_return': round(result['portfolio_return'], 4),
                'benchmark_return': round(result['benchmark_return'], 4),
                'excess_return': round(result['excess_return'], 4),
                'improvement_ratio': round(result['excess_return'] / abs(result['benchmark_return']) if result['benchmark_return'] != 0 else 0, 4)
            }
        
        # 保存报告
        report_path = os.path.join(DATA_DIR, 'backtest_report.csv')
        report_df = pd.DataFrame(report['detailed_results']).T
        report_df.to_csv(report_path)
        
        print(f"回测报告已保存到: {report_path}")
        return report

if __name__ == "__main__":
    # 测试代码
    import os
    from config import DATA_DIR
    
    # 加载预测数据
    data_path = os.path.join(DATA_DIR, 'prediction_results.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        
        analyzer = BacktestAnalyzer()
        results = analyzer.run_backtest(df)
        
        # 绘制图表
        analyzer.plot_performance_comparison()
        
        # 生成报告
        report = analyzer.generate_report()
        print("回测报告：")
        print(report)
    else:
        print("请先运行model_trainer.py进行预测")