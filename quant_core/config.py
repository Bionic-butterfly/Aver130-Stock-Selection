# 配置文件
import os

# 数据路径配置
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '../models')

# 创建必要的目录
for dir_path in [DATA_DIR, MODEL_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 时间范围配置
START_DATE = '2018-01-01'
END_DATE = '2023-12-31'

# 因子配置
FACTORS = {
    'pe_ttm': 'PE(TTM)',
    'pb_lf': 'PB(LF)', 
    'roe': 'ROE',
    'turnover_rate': '换手率',
    'total_mv': '总市值'
}

# 行业分类配置
INDUSTRY_MAP = {
    '银行': '金融',
    '非银金融': '金融',
    '房地产': '房地产',
    '医药生物': '医药',
    '食品饮料': '消费',
    '家用电器': '消费',
    '汽车': '制造',
    '电子': '科技',
    '计算机': '科技',
    '通信': '科技',
    '传媒': '传媒',
    '建筑装饰': '建筑',
    '钢铁': '材料',
    '有色金属': '材料',
    '化工': '材料',
    '公用事业': '公用事业',
    '交通运输': '交通',
    '农林牧渔': '农业',
    '国防军工': '军工',
    '机械设备': '制造',
    '电气设备': '制造',
    '轻工制造': '制造',
    '商业贸易': '商业',
    '休闲服务': '服务',
    '综合': '综合'
}

# XGBoost参数配置
XGB_PARAMS = {
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}