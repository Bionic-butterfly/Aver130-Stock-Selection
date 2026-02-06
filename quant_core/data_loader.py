# 数据加载模块
import pandas as pd
import numpy as np
from config import DATA_DIR, START_DATE, END_DATE, FACTORS
import os

class DataLoader:
    def __init__(self):
        # 使用模拟数据，避免tushare token依赖
        pass
        
    def get_hs300_constituents(self):
        """获取沪深300成分股"""
        file_path = os.path.join(DATA_DIR, 'hs300_constituents.csv')
        
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        
        # 模拟数据（实际使用时需要tushare token）
        # df = self.pro.index_weight(index_code='000300.SH', start_date=START_DATE, end_date=END_DATE)
        
        # 创建模拟数据
        dates = pd.date_range(START_DATE, END_DATE, freq='M')
        stocks = [f'{i:06d}.SZ' if i % 2 == 0 else f'{i:06d}.SH' for i in range(1, 301)]
        
        data = []
        for date in dates:
            for stock in stocks:
                data.append({
                    'trade_date': date.strftime('%Y%m%d'),
                    'con_code': stock,
                    'weight': np.random.uniform(0.1, 1.0)
                })
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return df
    
    def get_stock_data(self, ts_code, start_date, end_date):
        """获取个股数据"""
        # 模拟数据生成（实际使用时调用tushare接口）
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # 生成模拟价格数据
        prices = []
        base_price = np.random.uniform(10, 100)
        
        for i, date in enumerate(dates):
            # 模拟价格波动
            if i == 0:
                price = base_price
            else:
                change = np.random.normal(0, 0.02)  # 2%日波动
                price = prices[-1] * (1 + change)
            
            prices.append({
                'trade_date': date.strftime('%Y%m%d'),
                'ts_code': ts_code,
                'open': price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': price * (1 + np.random.uniform(0, 0.03)),
                'low': price * (1 + np.random.uniform(-0.03, 0)),
                'close': price,
                'vol': np.random.uniform(1000000, 10000000),
                'amount': price * np.random.uniform(1000000, 10000000)
            })
        
        return pd.DataFrame(prices)
    
    def get_factor_data(self, ts_code, trade_date):
        """获取因子数据"""
        # 模拟因子数据
        return {
            'pe_ttm': np.random.uniform(5, 50),  # PE(TTM)
            'pb_lf': np.random.uniform(0.5, 8),   # PB(LF)
            'roe': np.random.uniform(0.05, 0.3),  # ROE
            'turnover_rate': np.random.uniform(0.01, 0.1),  # 换手率
            'total_mv': np.random.uniform(1e9, 1e12)  # 总市值
        }
    
    def get_industry_info(self, ts_code):
        """获取行业信息"""
        industries = list(FACTORS.keys())
        return np.random.choice(industries)
    
    def prepare_training_data(self):
        """准备训练数据"""
        print("开始准备训练数据...")
        
        # 获取成分股
        constituents = self.get_hs300_constituents()
        
        # 生成训练数据
        training_data = []
        
        for _, row in constituents.iterrows():
            ts_code = row['con_code']
            trade_date = row['trade_date']
            
            # 获取因子数据
            factors = self.get_factor_data(ts_code, trade_date)
            
            # 获取价格数据计算收益率（作为目标变量）
            price_data = self.get_stock_data(ts_code, trade_date, trade_date)
            if len(price_data) > 0:
                # 模拟未来收益率
                future_return = np.random.normal(0, 0.1)
                
                data_point = {
                    'trade_date': trade_date,
                    'ts_code': ts_code,
                    'industry': self.get_industry_info(ts_code),
                    'future_return': future_return
                }
                data_point.update(factors)
                
                training_data.append(data_point)
        
        df = pd.DataFrame(training_data)
        
        # 保存数据
        file_path = os.path.join(DATA_DIR, 'training_data.csv')
        df.to_csv(file_path, index=False)
        
        print(f"训练数据准备完成，共{len(df)}条记录")
        return df

if __name__ == "__main__":
    loader = DataLoader()
    data = loader.prepare_training_data()
    print("数据样例：")
    print(data.head())