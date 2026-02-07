# 沪深300多因子选股系统 - 高级因子分析模块
# 【优化新增】支持分行业因子分析、IR信息比率计算、因子分位数单调性检验

import pandas as pd
import numpy as np
import os
import yaml
import logging
from sklearn.linear_model import LinearRegression

class FactorAnalyzerAdvanced:
    def __init__(self, config_file='config_advanced.yaml'):
        """初始化因子分析器"""
        # 加载配置
        self.config = self._load_config(config_file)
        self.logger = logging.getLogger(__name__)
        
        # 提取配置参数
        self.factors = self.config['factors']['selected_factors']
        self.factor_names = self.config['factors']['factor_names']
        self.industry_map = self.config['industry']['industry_map']
        self.winsorize_lower = self.config['factors']['winsorize']['lower']
        self.winsorize_upper = self.config['factors']['winsorize']['upper']
        self.industry_standardization_enabled = self.config['factors']['industry_standardization']['enabled']
    
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    def winsorize(self, series, lower=None, upper=None):
        """缩尾处理"""
        lower = lower or self.winsorize_lower
        upper = upper or self.winsorize_upper
        
        q_low = series.quantile(lower)
        q_high = series.quantile(upper)
        return np.clip(series, q_low, q_high)
    
    def standardize(self, series):
        """标准化处理"""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return series - mean
        return (series - mean) / std
    
    def industry_neutralization(self, df, factor_name):
        """行业中性化处理"""
        self.logger.info(f"正在进行 {factor_name} 的行业中性化处理...")
        
        # 行业映射
        df['industry_group'] = df['industry'].map(self.industry_map)
        
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
            self.logger.warning(f"中性化值长度({len(neutralized_values)})与数据长度({len(df)})不匹配，使用零填充")
            neutralized_values = [0] * len(df)
        
        return neutralized_values
    
    def industry_standardization(self, df, factor_name):
        """分行业独立标准化处理"""
        self.logger.info(f"正在进行 {factor_name} 的分行业标准化处理...")
        
        # 行业映射
        df['industry_group'] = df['industry'].map(self.industry_map)
        
        # 对每个行业进行独立标准化
        standardized_values = []
        
        for industry in df['industry_group'].unique():
            industry_data = df[df['industry_group'] == industry].copy()
            
            if len(industry_data) > 1:
                # 提取因子值
                factor_values = industry_data[factor_name].values
                
                # 标准化
                standardized = self.standardize(factor_values)
                standardized_values.extend(standardized)
            else:
                standardized_values.extend([0] * len(industry_data))
        
        # 确保返回值的长度与DataFrame一致
        if len(standardized_values) != len(df):
            # 如果长度不匹配，使用全局标准化
            self.logger.warning(f"分行业标准化值长度({len(standardized_values)})与数据长度({len(df)})不匹配，使用全局标准化")
            standardized_values = self.standardize(df[factor_name]).tolist()
        
        return standardized_values
    
    def process_factors(self, df):
        """因子处理主函数"""
        self.logger.info("开始因子处理...")
        
        # 复制数据
        processed_df = df.copy()
        
        # 对每个因子进行处理
        for factor in self.factors:
            if factor in processed_df.columns:
                self.logger.info(f"处理因子: {factor}")
                
                # 1. 缩尾处理
                processed_df[f'{factor}_winsorized'] = self.winsorize(processed_df[factor])
                
                # 2. 行业中性化
                neutralized = self.industry_neutralization(processed_df, f'{factor}_winsorized')
                processed_df[f'{factor}_neutral'] = neutralized
                
                # 3. 分行业标准化（如果启用）
                if self.industry_standardization_enabled:
                    standardized = self.industry_standardization(processed_df, f'{factor}_neutral')
                    processed_df[f'{factor}_neutral_std'] = standardized
                else:
                    # 全局标准化
                    processed_df[f'{factor}_neutral_std'] = self.standardize(processed_df[f'{factor}_neutral'])
                
                self.logger.info(f"因子 {factor} 处理完成")
        
        return processed_df
    
    def calculate_ic(self, df):
        """计算因子IC值"""
        self.logger.info("计算因子IC值...")
        ic_results = {}
        
        for factor in self.factors:
            neutral_factor = f'{factor}_neutral_std'
            if neutral_factor in df.columns:
                # 计算IC值（因子值与未来收益率的相关系数）
                ic = df[neutral_factor].corr(df['future_return'])
                ic_results[factor] = ic
                self.logger.info(f"因子 {factor} 的IC值: {ic:.4f}")
        
        return ic_results
    
    def calculate_ir(self, df):
        """计算因子IR信息比率"""
        self.logger.info("计算因子IR信息比率...")
        ir_results = {}
        
        for factor in self.factors:
            neutral_factor = f'{factor}_neutral_std'
            if neutral_factor in df.columns:
                # 计算IC值
                ic = df[neutral_factor].corr(df['future_return'])
                
                # 计算因子标准差
                factor_std = df[neutral_factor].std()
                
                # 计算IR信息比率
                ir = ic / factor_std if factor_std != 0 else 0
                ir_results[factor] = ir
                self.logger.info(f"因子 {factor} 的IR信息比率: {ir:.4f}")
        
        return ir_results
    
    def calculate_monotonicity(self, df):
        """计算因子分位数单调性"""
        self.logger.info("计算因子分位数单调性...")
        monotonicity_results = {}
        
        for factor in self.factors:
            neutral_factor = f'{factor}_neutral_std'
            if neutral_factor in df.columns:
                # 计算单调性
                monotonicity = self._calculate_monotonicity_score(df, neutral_factor, 'future_return')
                monotonicity_results[factor] = monotonicity
                self.logger.info(f"因子 {factor} 的单调性得分: {monotonicity:.4f}")
        
        return monotonicity_results
    
    def _calculate_monotonicity_score(self, df, factor_col, target_col):
        """计算单个因子的分位数单调性得分"""
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
            self.logger.error(f"计算单调性得分失败: {e}")
            return 0
    
    def analyze_factors_by_industry(self, df):
        """分行业因子分析"""
        self.logger.info("开始分行业因子分析...")
        
        industry_analysis_results = []
        
        # 按行业分组分析
        for industry in df['industry'].unique():
            industry_data = df[df['industry'] == industry].copy()
            
            if len(industry_data) < 10:  # 跳过样本量不足的行业
                self.logger.warning(f"行业 {industry} 样本量不足，跳过分析")
                continue
            
            self.logger.info(f"分析行业: {industry}")
            
            for factor in self.factors:
                neutral_factor = f'{factor}_neutral_std'
                if neutral_factor in industry_data.columns:
                    # 计算IC值
                    ic = industry_data[neutral_factor].corr(industry_data['future_return'])
                    
                    # 计算IR信息比率
                    factor_std = industry_data[neutral_factor].std()
                    ir = ic / factor_std if factor_std != 0 else 0
                    
                    # 计算单调性
                    monotonicity = self._calculate_monotonicity_score(industry_data, neutral_factor, 'future_return')
                    
                    industry_analysis_results.append({
                        'industry': industry,
                        'factor': factor,
                        'factor_name': self.factor_names.get(factor, factor),
                        'ic_mean': float(ic),
                        'ic_std': float(factor_std),
                        'ir': float(ir),
                        'monotonicity': float(monotonicity),
                        'sample_size': len(industry_data)
                    })
        
        return industry_analysis_results
    
    def generate_factor_report(self, df):
        """生成因子分析报告"""
        self.logger.info("生成因子分析报告...")
        
        report = {
            'overall': {
                'ic_values': self.calculate_ic(df),
                'ir_values': self.calculate_ir(df),
                'monotonicity': self.calculate_monotonicity(df)
            },
            'by_industry': self.analyze_factors_by_industry(df)
        }
        
        # 保存报告
        report_df = pd.DataFrame(report['by_industry'])
        file_path = os.path.join(self.config['data']['data_dir'], self.config['data']['industry_factor_analysis_file'])
        report_df.to_csv(file_path, index=False)
        self.logger.info(f"因子分析报告已保存到: {file_path}")
        
        return report
    
    def get_factor_importance(self, model, feature_columns):
        """获取因子重要性"""
        try:
            # 获取特征重要性
            importance = model.feature_importances_
            
            # 映射到原始因子
            factor_importance = {}
            for i, feature in enumerate(feature_columns):
                # 提取原始因子名称
                factor_name = feature.replace('_neutral_std', '')
                factor_importance[factor_name] = float(importance[i])
            
            # 排序
            sorted_importance = dict(sorted(factor_importance.items(), key=lambda x: x[1], reverse=True))
            
            self.logger.info("因子重要性排序:")
            for factor, imp in sorted_importance.items():
                self.logger.info(f"  {factor}: {imp:.4f}")
            
            return sorted_importance
            
        except Exception as e:
            self.logger.error(f"获取因子重要性失败: {e}")
            return {}
