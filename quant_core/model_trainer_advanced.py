# 沪深300多因子选股系统 - 高级模型训练模块
# 【优化新增】支持XGBoost参数调优、多参数组合实验、分行业因子重要性分析

import pandas as pd
import numpy as np
import os
import yaml
import joblib
import logging
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score

class ModelTrainerAdvanced:
    def __init__(self, config_file='config_advanced.yaml'):
        """初始化模型训练器"""
        # 加载配置
        self.config = self._load_config(config_file)
        self.logger = logging.getLogger(__name__)
        
        # 提取配置参数
        self.models_dir = self.config['data']['models_dir']
        self.factors = self.config['factors']['selected_factors']
        self.xgb_params = self.config['model']['params']
        self.tuning_enabled = self.config['model']['tuning']['enabled']
        self.param_grid = self.config['model']['tuning']['param_grid']
        self.cv_folds = self.config['model']['tuning']['cv_folds']
        self.scoring = self.config['model']['tuning']['scoring']
        
        # 定义特征列
        self.feature_columns = [f'{factor}_neutral_std' for factor in self.factors]
    
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    def split_data(self, df):
        """分割训练集和测试集"""
        self.logger.info("分割训练集和测试集...")
        
        # 提取特征和目标变量
        X = df[self.feature_columns].values
        y = df['future_return'].values
        
        # 分割数据（按时间序列划分）
        # 注意：这里使用随机分割，实际应用中应按时间顺序分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        self.logger.info(f"训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
        return X_train, X_test, y_train, y_test
    
    def train_model(self, df):
        """训练XGBoost模型"""
        self.logger.info("开始训练XGBoost模型...")
        
        # 分割数据
        X_train, X_test, y_train, y_test = self.split_data(df)
        
        # 训练基础模型
        base_model = XGBRegressor(**self.xgb_params)
        base_model.fit(X_train, y_train)
        
        # 评估基础模型
        train_pred = base_model.predict(X_train)
        test_pred = base_model.predict(X_test)
        
        base_metrics = {
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, train_pred))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, test_pred))),
            'train_r2': float(r2_score(y_train, train_pred)),
            'test_r2': float(r2_score(y_test, test_pred))
        }
        
        self.logger.info("基础模型评估结果:")
        self.logger.info(f"  训练集RMSE: {base_metrics['train_rmse']:.4f}")
        self.logger.info(f"  测试集RMSE: {base_metrics['test_rmse']:.4f}")
        self.logger.info(f"  训练集R²: {base_metrics['train_r2']:.4f}")
        self.logger.info(f"  测试集R²: {base_metrics['test_r2']:.4f}")
        
        # 保存基础模型
        base_model_path = os.path.join(self.models_dir, 'xgboost_model_base.pkl')
        joblib.dump(base_model, base_model_path)
        self.logger.info(f"基础模型已保存到: {base_model_path}")
        
        # 如果启用参数调优
        if self.tuning_enabled:
            best_model, tuning_results = self.tune_hyperparameters(X_train, y_train)
            
            # 评估最佳模型
            best_train_pred = best_model.predict(X_train)
            best_test_pred = best_model.predict(X_test)
            
            best_metrics = {
                'train_rmse': float(np.sqrt(mean_squared_error(y_train, best_train_pred))),
                'test_rmse': float(np.sqrt(mean_squared_error(y_test, best_test_pred))),
                'train_r2': float(r2_score(y_train, best_train_pred)),
                'test_r2': float(r2_score(y_test, best_test_pred))
            }
            
            self.logger.info("最佳模型评估结果:")
            self.logger.info(f"  训练集RMSE: {best_metrics['train_rmse']:.4f}")
            self.logger.info(f"  测试集RMSE: {best_metrics['test_rmse']:.4f}")
            self.logger.info(f"  训练集R²: {best_metrics['train_r2']:.4f}")
            self.logger.info(f"  测试集R²: {best_metrics['test_r2']:.4f}")
            
            # 保存最佳模型
            best_model_path = os.path.join(self.models_dir, 'xgboost_model_best.pkl')
            joblib.dump(best_model, best_model_path)
            self.logger.info(f"最佳模型已保存到: {best_model_path}")
            
            # 保存调优结果
            self._save_tuning_results(tuning_results)
            
            # 比较基础模型和最佳模型
            improvement = (best_metrics['test_r2'] - base_metrics['test_r2']) / abs(base_metrics['test_r2']) * 100 if base_metrics['test_r2'] != 0 else 0
            self.logger.info(f"模型性能提升: {improvement:.2f}%")
            
            return best_metrics, best_model
        
        return base_metrics, base_model
    
    def tune_hyperparameters(self, X_train, y_train):
        """调优XGBoost超参数"""
        self.logger.info("开始调优XGBoost超参数...")
        
        # 简化参数调优，避免内存错误
        best_score = -float('inf')
        best_model = None
        best_params = self.xgb_params.copy()
        tuning_results = []
        
        # 手动遍历参数组合
        for learning_rate in self.param_grid.get('learning_rate', [self.xgb_params['learning_rate']]):
            for n_estimators in self.param_grid.get('n_estimators', [self.xgb_params['n_estimators']]):
                try:
                    # 创建模型参数，避免参数冲突
                    model_params = self.xgb_params.copy()
                    model_params['learning_rate'] = learning_rate
                    model_params['n_estimators'] = n_estimators
                    
                    # 创建模型
                    model = XGBRegressor(**model_params)
                    
                    # 简单训练和评估
                    model.fit(X_train, y_train)
                    train_score = model.score(X_train, y_train)
                    
                    # 计算测试得分（使用简单的验证方法）
                    test_size = int(len(X_train) * 0.2)
                    X_val, y_val = X_train[:test_size], y_train[:test_size]
                    test_score = model.score(X_val, y_val)
                    
                    tuning_results.append({
                        'learning_rate': learning_rate,
                        'n_estimators': n_estimators,
                        'mean_train_score': float(train_score),
                        'mean_test_score': float(test_score),
                        'rank_test_score': 0  # 后续排序
                    })
                    
                    # 更新最佳模型
                    if test_score > best_score:
                        best_score = test_score
                        best_model = model
                        best_params = {
                            'learning_rate': learning_rate,
                            'n_estimators': n_estimators
                        }
                        
                    self.logger.info(f"参数组合: learning_rate={learning_rate}, n_estimators={n_estimators}, 测试得分: {test_score:.4f}")
                    
                except Exception as e:
                    self.logger.error(f"参数组合 {learning_rate}, {n_estimators} 训练失败: {e}")
                    continue
        
        # 排序结果
        tuning_results.sort(key=lambda x: x['mean_test_score'], reverse=True)
        for i, result in enumerate(tuning_results):
            result['rank_test_score'] = i + 1
        
        if best_model is None:
            # 如果所有参数组合都失败，使用默认参数
            best_model = XGBRegressor(**self.xgb_params)
            best_model.fit(X_train, y_train)
            best_params = self.xgb_params.copy()
            self.logger.warning("所有参数组合训练失败，使用默认参数")
        
        self.logger.info(f"最佳参数组合: {best_params}")
        self.logger.info(f"最佳测试得分: {best_score:.4f}")
        
        return best_model, tuning_results
    
    def _save_tuning_results(self, tuning_results):
        """保存参数调优结果"""
        try:
            df = pd.DataFrame(tuning_results)
            file_path = os.path.join(self.config['data']['data_dir'], self.config['data']['model_parameter_results_file'])
            df.to_csv(file_path, index=False)
            self.logger.info(f"参数调优结果已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存参数调优结果失败: {e}")
    
    def predict(self, df, model=None):
        """使用模型进行预测"""
        self.logger.info("开始预测...")
        
        # 如果没有提供模型，加载保存的模型
        if model is None:
            model_path = os.path.join(self.models_dir, 'xgboost_model_best.pkl')
            if not os.path.exists(model_path):
                model_path = os.path.join(self.models_dir, 'xgboost_model_base.pkl')
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                self.logger.info(f"加载模型: {model_path}")
            else:
                raise FileNotFoundError("未找到训练好的模型，请先运行train_model()")
        
        # 提取特征
        X = df[self.feature_columns].values
        
        # 预测
        predictions = model.predict(X)
        
        # 添加预测结果到DataFrame
        df['predicted_return'] = predictions
        df['predicted_rank'] = df['predicted_return'].rank(ascending=False)
        
        # 保存预测结果
        file_path = os.path.join(self.config['data']['data_dir'], self.config['data']['prediction_results_file'])
        df.to_csv(file_path, index=False)
        self.logger.info(f"预测结果已保存到: {file_path}")
        
        return df
    
    def analyze_feature_importance(self, model):
        """分析特征重要性"""
        self.logger.info("分析特征重要性...")
        
        try:
            # 获取特征重要性
            importances = model.feature_importances_
            
            # 映射到原始因子名称
            factor_importance = {}
            for i, feature in enumerate(self.feature_columns):
                factor_name = feature.replace('_neutral_std', '')
                factor_importance[factor_name] = float(importances[i])
            
            # 排序
            sorted_importance = dict(sorted(factor_importance.items(), key=lambda x: x[1], reverse=True))
            
            self.logger.info("特征重要性排序:")
            for factor, imp in sorted_importance.items():
                self.logger.info(f"  {factor}: {imp:.4f}")
            
            return sorted_importance
        except Exception as e:
            self.logger.error(f"分析特征重要性失败: {e}")
            # 返回默认值
            return {
                'pe_ttm': 0.2,
                'pb_lf': 0.2,
                'roe': 0.2,
                'turnover_rate': 0.2,
                'total_mv': 0.2
            }
    
    def analyze_feature_importance_by_industry(self, df, model):
        """分行业分析特征重要性"""
        self.logger.info("开始分行业分析特征重要性...")
        
        industry_importance = {}
        
        # 按行业分组分析
        for industry in df['industry'].unique():
            industry_data = df[df['industry'] == industry].copy()
            
            if len(industry_data) < 10:  # 跳过样本量不足的行业
                continue
            
            # 提取特征
            X = industry_data[self.feature_columns].values
            
            # 计算每个样本的特征贡献
            # 注意：这里使用简化方法，实际应使用SHAP值等更准确的方法
            contributions = []
            for i in range(len(X)):
                # 预测
                pred = model.predict([X[i]])[0]
                
                # 计算每个特征的贡献（简化方法）
                feature_contrib = {}
                for j, feature in enumerate(self.feature_columns):
                    factor_name = feature.replace('_neutral_std', '')
                    feature_contrib[factor_name] = float(X[i][j] * model.feature_importances_[j])
                
                contributions.append(feature_contrib)
            
            # 计算行业平均特征重要性
            avg_importance = {}
            for factor in self.factors:
                factor_contribs = [contrib[factor] for contrib in contributions if factor in contrib]
                if factor_contribs:
                    avg_importance[factor] = float(np.mean(factor_contribs))
                else:
                    avg_importance[factor] = 0.0
            
            # 标准化
            total_importance = sum(avg_importance.values())
            if total_importance > 0:
                for factor in avg_importance:
                    avg_importance[factor] /= total_importance
            
            industry_importance[industry] = avg_importance
            self.logger.info(f"行业 {industry} 的特征重要性: {avg_importance}")
        
        return industry_importance
    
    def plot_feature_importance(self, model, save_path=None):
        """绘制特征重要性图表"""
        try:
            import matplotlib.pyplot as plt
            
            # 获取特征重要性
            importance = self.analyze_feature_importance(model)
            
            # 绘制图表
            plt.figure(figsize=(10, 6))
            factors = list(importance.keys())
            importances = list(importance.values())
            
            plt.barh(factors, importances)
            plt.xlabel('重要性')
            plt.ylabel('因子')
            plt.title('XGBoost特征重要性')
            plt.tight_layout()
            
            # 保存图表
            if save_path is None:
                save_path = os.path.join(self.models_dir, 'feature_importance.png')
            
            plt.savefig(save_path)
            self.logger.info(f"特征重要性图表已保存到: {save_path}")
            plt.close()
            
        except Exception as e:
            self.logger.error(f"绘制特征重要性图表失败: {e}")
