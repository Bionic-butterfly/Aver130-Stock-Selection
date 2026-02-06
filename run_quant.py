#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化核心运行脚本
运行命令: python run_quant.py
"""

import sys
import os

# 添加量化核心模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'quant_core'))

def main():
    """运行量化核心模块"""
    print("=== 沪深300多因子选股系统 - 量化核心模块 ===")
    print("正在启动量化核心...")
    
    try:
        # 导入并运行量化核心
        from quant_core.main import main as quant_main
        results = quant_main()
        
        print("\n✅ 量化核心执行成功!")
        print("📊 输出文件:")
        print(f"   - 原始数据: {results['raw_data']}")
        print(f"   - 处理数据: {results['processed_data']}")
        print(f"   - 预测结果: {results['predictions']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 量化核心已完成，现在可以启动后端和前端服务!")
        print("\n📋 下一步操作:")
        print("1. 启动后端服务: cd backend && python main.py")
        print("2. 启动前端服务: cd frontend && npm run dev")
        print("3. 访问系统: http://localhost:3000")
    else:
        print("\n❌ 量化核心执行失败，请检查错误信息")