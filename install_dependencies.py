#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键安装依赖脚本
运行命令: python install_dependencies.py
"""

import subprocess
import sys
import os

def run_command(command, cwd=None):
    """运行命令并显示输出"""
    print(f"🚀 执行命令: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'  # 忽略编码错误
        )
        if result.returncode == 0:
            print("✅ 执行成功")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 执行失败")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 命令执行异常: {e}")
        return False

def main():
    """主安装函数"""
    print("=== 沪深300多因子选股系统 - 依赖安装 ===")
    print()
    
    # 1. 安装量化核心依赖
    print("📦 步骤1: 安装量化核心依赖")
    print("-" * 50)
    if not run_command("pip install -r requirements.txt", "quant_core"):
        print("❌ 量化核心依赖安装失败")
        return False
    print()
    
    # 2. 安装后端依赖
    print("📦 步骤2: 安装后端依赖")
    print("-" * 50)
    if not run_command("pip install -r requirements.txt", "backend"):
        print("❌ 后端依赖安装失败")
        return False
    print()
    
    # 3. 安装前端依赖
    print("📦 步骤3: 安装前端依赖")
    print("-" * 50)
    if not run_command("npm install", "frontend"):
        print("❌ 前端依赖安装失败")
        return False
    print()
    
    print("🎉 所有依赖安装完成!")
    print()
    print("📋 下一步操作:")
    print("1. 运行量化核心: python run_quant.py")
    print("2. 启动后端服务: cd backend && python main.py")
    print("3. 启动前端服务: cd frontend && npm run dev")
    print("4. 访问系统: http://localhost:3000")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)