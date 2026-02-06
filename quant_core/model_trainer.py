# 模型训练模块
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from config import MODEL_DIR, XGB_PARAMS
import os

class ModelTrainer:
    def __init__(self):
        self.model = None
        self.feature_columns = []
        
    def prepare_features(self, df):
        """准备特征数据"""
        # 选择中性化标准化后的因子作为特征
        feature_columns = [f'{factor}_neutral_std' for factor in ['pe_ttm', 'pb_lf', 'roe', 'turnover_rate', 'total_mv']]
        
        # 确保所有特征列都存在
        available_features = [col for col in feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("没有找到可用的特征列")
        
        self.feature_columns = available_features
        
        # 准备特征和目标变量
        X = df[available_features].values
        y = df['future_return'].values
        
        return X, y
    
    def train_model(self, df):
        """训练XGBoost模型"""
        print("开始训练XGBoost模型...")
        
        # 准备数据
        X, y = self.prepare_features(df)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # 创建并训练模型
        self.model = XGBRegressor(**XGB_PARAMS)
        self.model.fit(X_train, y_train)
        
        # 模型评估
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"训练集RMSE: {train_rmse:.4f}, R²: {train_r2:.4f}")
        print(f"测试集RMSE: {test_rmse:.4f}, R²: {test_r2:.4f}")
        
        # 保存模型
        model_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
        joblib.dump(self.model, model_path)
        print(f"模型已保存到: {model_path}")
        
        return {
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
    
    def plot_feature_importance(self):
        """绘制特征重要性图"""
        if self.model is None:
            print("请先训练模型")
            return
        
        # 获取特征重要性
        importance = self.model.feature_importances_
        
        # 创建DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=True)
        
        # 绘制水平条形图
        plt.figure(figsize=(10, 6))
        plt.barh(importance_df['feature'], importance_df['importance'])
        plt.xlabel('特征重要性')
        plt.title('XGBoost模型特征重要性')
        plt.tight_layout()
        
        # 保存图片
        img_path = os.path.join(MODEL_DIR, 'feature_importance.png')
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"特征重要性图已保存到: {img_path}")
        
        return importance_df
    
    def predict(self, df):
        """使用模型进行预测"""
        if self.model is None:
            # 尝试加载已保存的模型
            model_path = os.path.join(MODEL_DIR, 'xgboost_model.pkl')
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("已加载预训练模型")
            else:
                raise ValueError("模型未训练，请先调用train_model方法")
        
        # 准备特征
        X, _ = self.prepare_features(df)
        
        # 预测
        predictions = self.model.predict(X)
        
        # 添加到数据中
        df['predicted_return'] = predictions
        df['predicted_rank'] = df['predicted_return'].rank(ascending=False)
        
        return df

if __name__ == "__main__":
    # 测试代码
    import os
    from config import DATA_DIR
    
    # 加载处理后的数据
    data_path = os.path.join(DATA_DIR, 'processed_data.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        
        trainer = ModelTrainer()
        metrics = trainer.train_model(df)
        
        # 绘制特征重要性
        importance_df = trainer.plot_feature_importance()
        print("特征重要性排序：")
        print(importance_df)
        
        # 进行预测
        predictions = trainer.predict(df)
        print("预测结果样例：")
        print(predictions[['ts_code', 'predicted_return', 'predicted_rank']].head())
    else:
        print("请先运行factor_processor.py处理数据")