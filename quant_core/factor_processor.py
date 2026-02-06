# 因子处理模块
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from config import FACTORS, INDUSTRY_MAP
import warnings
warnings.filterwarnings('ignore')

class FactorProcessor:
    def __init__(self):
        self.factors = list(FACTORS.keys())
        
    def winsorize(self, series, lower=0.05, upper=0.95):
        """缩尾处理"""
        q_low = series.quantile(lower)
        q_high = series.quantile(upper)
        return np.clip(series, q_low, q_high)
    
    def standardize(self, series):
        """标准化处理"""
        return (series - series.mean()) / series.std()
    
    def industry_neutralization(self, df, factor_name):
        """行业中性化处理"""
        print(f"正在进行 {factor_name} 的行业中性化处理...")
        
        # 行业映射
        df['industry_group'] = df['industry'].map(INDUSTRY_MAP)
        
        # 对每个行业进行回归中性化
        neutralized_values = []
        
        for industry in df['industry_group'].unique():
            industry_data = df[df['industry_group'] == industry].copy()
            
            if len(industry_data) > 1:
                # 提取因子值
                X = industry_data[[factor_name]].values
                y = industry_data[factor_name].values
                
                # 线性回归
                model = LinearRegression()
                model.fit(X, y)
                
                # 计算残差（中性化后的因子值）
                residuals = y - model.predict(X)
                neutralized_values.extend(residuals)
            else:
                neutralized_values.extend([0] * len(industry_data))
        
        # 确保返回值的长度与DataFrame一致
        if len(neutralized_values) != len(df):
            # 如果长度不匹配，使用零填充
            print(f"警告: 中性化值长度({len(neutralized_values)})与数据长度({len(df)})不匹配，使用零填充")
            neutralized_values = [0] * len(df)
        
        return neutralized_values
    
    def process_factors(self, df):
        """因子处理主函数"""
        print("开始因子处理...")
        
        # 复制数据
        processed_df = df.copy()
        
        # 对每个因子进行处理
        for factor in self.factors:
            if factor in processed_df.columns:
                # 1. 缩尾处理
                processed_df[factor] = self.winsorize(processed_df[factor])
                
                # 2. 行业中性化
                neutralized = self.industry_neutralization(processed_df, factor)
                processed_df[f'{factor}_neutral'] = neutralized
                
                # 3. 标准化
                processed_df[f'{factor}_neutral_std'] = self.standardize(
                    processed_df[f'{factor}_neutral']
                )
                
                print(f"因子 {factor} 处理完成")
        
        return processed_df
    
    def calculate_ic(self, df):
        """计算因子IC值"""
        ic_results = {}
        
        for factor in self.factors:
            neutral_factor = f'{factor}_neutral_std'
            if neutral_factor in df.columns:
                # 计算IC值（因子值与未来收益率的相关系数）
                ic = df[neutral_factor].corr(df['future_return'])
                ic_results[factor] = ic
        
        return ic_results

if __name__ == "__main__":
    # 测试代码
    import os
    from config import DATA_DIR
    
    # 加载数据
    data_path = os.path.join(DATA_DIR, 'training_data.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        
        processor = FactorProcessor()
        processed_df = processor.process_factors(df)
        
        ic_results = processor.calculate_ic(processed_df)
        print("因子IC值：")
        for factor, ic in ic_results.items():
            print(f"{factor}: {ic:.4f}")
    else:
        print("请先运行data_loader.py生成训练数据")