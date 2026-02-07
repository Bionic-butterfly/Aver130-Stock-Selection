# 沪深300多因子选股系统 - 高级数据加载模块
# 【优化新增】支持2019-2026年数据范围，新增分行业因子分析数据生成

import pandas as pd
import numpy as np
import os
import yaml
import json
import logging
from datetime import datetime, timedelta

class DataLoaderAdvanced:
    def __init__(self, config_file='config_advanced.yaml'):
        """初始化数据加载器"""
        # 加载配置
        self.config = self._load_config(config_file)
        self.logger = logging.getLogger(__name__)
        
        # 创建必要的目录
        self._create_directories()
        
        # 提取配置参数
        self.start_date = self.config['basic']['start_date']
        self.end_date = self.config['basic']['end_date']
        self.data_dir = self.config['data']['data_dir']
        self.factors = self.config['factors']['selected_factors']
        
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.config['data']['data_dir'],
            self.config['data']['models_dir'],
            self.config['data']['logs_dir']
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"创建目录: {directory}")
    
    def get_hs300_constituents(self):
        """获取沪深300成分股"""
        file_path = os.path.join(self.data_dir, self.config['data']['hs300_constituents_file'])
        
        if os.path.exists(file_path):
            self.logger.info(f"加载成分股数据: {file_path}")
            return pd.read_csv(file_path)
        
        self.logger.info("生成模拟成分股数据...")
        # 生成模拟数据
        dates = pd.date_range(self.start_date, self.end_date, freq='M')
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
        self.logger.info(f"成分股数据已保存: {file_path}")
        return df
    
    def get_stock_data(self, ts_code, start_date, end_date):
        """获取个股数据"""
        # 模拟数据生成
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
                price = prices[-1]['close'] * (1 + change)
            
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
        industries = list(self.config['industry']['industry_map'].keys())
        return np.random.choice(industries)
    
    def prepare_training_data(self):
        """准备训练数据"""
        self.logger.info("开始准备训练数据...")
        
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
        file_path = os.path.join(self.data_dir, self.config['data']['training_data_file'])
        df.to_csv(file_path, index=False)
        self.logger.info(f"训练数据准备完成，共{len(df)}条记录，已保存到: {file_path}")
        
        # 生成数据质量报告
        self._generate_data_quality_report(df)
        
        return df
    
    def _generate_data_quality_report(self, df):
        """生成数据质量报告"""
        try:
            report = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_summary': {
                    'total_records': len(df),
                    'unique_stocks': df['ts_code'].nunique(),
                    'unique_industries': df['industry'].nunique(),
                    'date_range': {
                        'start': df['trade_date'].min() if not df.empty else None,
                        'end': df['trade_date'].max() if not df.empty else None
                    }
                },
                'factor_quality': {},
                'data_integrity': {
                    'missing_values': {
                        col: int(df[col].isnull().sum())
                        for col in df.columns
                    },
                    'duplicate_records': int(df.duplicated().sum())
                }
            }
            
            # 计算因子质量指标
            for factor in self.factors:
                if factor in df.columns:
                    report['factor_quality'][factor] = {
                        'mean': float(df[factor].mean()),
                        'std': float(df[factor].std()),
                        'min': float(df[factor].min()),
                        'max': float(df[factor].max()),
                        'missing_values': int(df[factor].isnull().sum())
                    }
            
            # 保存数据质量报告
            report_file = os.path.join(self.data_dir, self.config['data']['data_quality_report_file'])
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据质量报告已生成: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成数据质量报告失败: {e}")
    
    def prepare_industry_factor_data(self, processed_data):
        """准备分行业因子分析数据"""
        self.logger.info("开始准备分行业因子分析数据...")
        
        try:
            industry_factor_data = []
            
            # 按行业分组分析
            for industry in processed_data['industry'].unique():
                industry_data = processed_data[processed_data['industry'] == industry]
                
                if len(industry_data) < 10:  # 跳过样本量不足的行业
                    continue
                
                for factor in self.factors:
                    neutral_factor = f'{factor}_neutral_std'
                    if neutral_factor in industry_data.columns:
                        # 计算IC值
                        ic = industry_data[neutral_factor].corr(industry_data['future_return'])
                        
                        # 计算IR信息比率
                        ic_mean = ic
                        ic_std = industry_data[neutral_factor].std()
                        ir = ic_mean / ic_std if ic_std != 0 else 0
                        
                        # 计算分位数单调性
                        monotonicity = self._calculate_monotonicity(industry_data, neutral_factor, 'future_return')
                        
                        industry_factor_data.append({
                            'industry': industry,
                            'factor': factor,
                            'ic_mean': float(ic_mean),
                            'ic_std': float(ic_std),
                            'ir': float(ir),
                            'monotonicity': float(monotonicity),
                            'sample_size': len(industry_data)
                        })
            
            # 保存分行业因子分析数据
            df = pd.DataFrame(industry_factor_data)
            file_path = os.path.join(self.data_dir, self.config['data']['industry_factor_analysis_file'])
            df.to_csv(file_path, index=False)
            self.logger.info(f"分行业因子分析数据已生成，共{len(df)}条记录，已保存到: {file_path}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"准备分行业因子分析数据失败: {e}")
            return pd.DataFrame()
    
    def _calculate_monotonicity(self, df, factor_col, target_col):
        """计算因子分位数单调性"""
        try:
            # 将因子值分为5个分位数
            df['quantile'] = pd.qcut(df[factor_col], 5, labels=False, duplicates='drop')
            
            # 计算每个分位数的平均目标值
            quantile_means = df.groupby('quantile')[target_col].mean().sort_index()
            
            # 计算单调性得分（皮尔逊相关系数）
            if len(quantile_means) >= 2:
                x = np.arange(len(quantile_means))
                y = quantile_means.values
                monotonicity = np.corrcoef(x, y)[0, 1]
            else:
                monotonicity = 0
            
            return monotonicity
            
        except Exception as e:
            self.logger.error(f"计算单调性失败: {e}")
            return 0
    
    def get_market_regimes(self):
        """获取市场阶段划分"""
        # 模拟市场阶段划分
        regimes = [
            {'start_date': '20190101', 'end_date': '20200220', 'regime': 'bull'},
            {'start_date': '20200221', 'end_date': '20200320', 'regime': 'bear'},
            {'start_date': '20200321', 'end_date': '20211231', 'regime': 'bull'},
            {'start_date': '20220101', 'end_date': '20221031', 'regime': 'bear'},
            {'start_date': '20221101', 'end_date': '20231231', 'regime': 'neutral'},
            {'start_date': '20240101', 'end_date': '20241231', 'regime': 'bull'},
            {'start_date': '20250101', 'end_date': '20260205', 'regime': 'neutral'}
        ]
        return regimes

if __name__ == "__main__":
    # 测试数据加载器
    loader = DataLoaderAdvanced()
    data = loader.prepare_training_data()
    print("数据样例：")
    print(data.head())
    print(f"数据形状：{data.shape}")
